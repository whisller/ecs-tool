import arrow

from ...context import ContextObject
from ...data_loader import fetch_listing as base_fetch_listing
from ...utils import _paginate


def _fetch_cloudwatch(cloudwatch, metrics_name, cluster_name, service_name):
    data = cloudwatch.get_metric_statistics(
        Namespace="AWS/ECS",
        MetricName=metrics_name,
        Dimensions=[
            {"Name": "ClusterName", "Value": cluster_name},
            {"Name": "ServiceName", "Value": service_name},
        ],
        StartTime=arrow.get().shift(hours=-24).datetime,
        EndTime=arrow.get().datetime,
        Period=3600,
        Statistics=["Average"],
    )
    return list(sorted(data["Datapoints"], key=lambda v: v["Timestamp"]))


def fetch_listing(context: ContextObject, click_params):
    return base_fetch_listing(
        context.ecs,
        paginator_type="list_services",
        arn_index="serviceArns",
        describe_function=context.ecs.describe_services,
        describe_filter="services",
        result_key="services",
        paginator_params={"cluster": click_params["cluster"]},
    )


def fetch_dashboard(context: ContextObject, click_params):
    services = context.ecs.describe_services(cluster=click_params["cluster"], services=[click_params["service"]])

    tasks_pagination = _paginate(
        context.ecs,
        "list_tasks",
        cluster=click_params["cluster"],
        desiredStatus="RUNNING",
        serviceName=click_params["service"],
    )

    arns = []
    for iterator in tasks_pagination:
        for task in iterator:
            arns += task["taskArns"]

    if not arns:
        return {"services": services}
    described_tasks = context.ecs.describe_tasks(cluster=click_params["cluster"], tasks=arns)

    cloudwatch_memory_data = _fetch_cloudwatch(
        context.cloudwatch,
        "MemoryUtilization",
        click_params["cluster"],
        click_params["service"],
    )
    cloudwatch_cpu_data = _fetch_cloudwatch(
        context.cloudwatch,
        "CPUUtilization",
        click_params["cluster"],
        click_params["service"],
    )

    task_definition = context.ecs.describe_task_definition(
        taskDefinition=described_tasks["tasks"][0]["taskDefinitionArn"]
    )

    log_configuration = task_definition["taskDefinition"]["containerDefinitions"][0]["logConfiguration"]
    describe_log_streams = context.logs.describe_log_streams(
        logGroupName=log_configuration["options"]["awslogs-group"],
        orderBy="LastEventTime",
        descending=True,
        limit=1,
    )
    log_events = context.logs.get_log_events(
        logGroupName=log_configuration["options"]["awslogs-group"],
        logStreamName=describe_log_streams["logStreams"][0]["logStreamName"],
        limit=100,
        startFromHead=False,
    )

    return {
        "services": services,
        "tasks": described_tasks,
        "cloudwatch_memory_data": cloudwatch_memory_data,
        "cloudwatch_cpu_data": cloudwatch_cpu_data,
        "logs": log_events,
    }
