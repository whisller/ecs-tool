import json

from ...context import ContextObject
from ...data_loader import fetch_listing as base_fetch_listing
from ...exception import EcsToolException


def _task_arn_helper(context: ContextObject, click_params):
    return f"arn:aws:ecs:{context.aws_region}:{context.aws_account_id}:task/{click_params['cluster']}/{click_params['task_id']}"


def _fetch_latest_active_task_definition(ecs_client, name):
    response = ecs_client.list_task_definitions(familyPrefix=name, status="ACTIVE", sort="DESC", maxResults=1)

    if not response["taskDefinitionArns"]:
        raise EcsToolException(f'Unable to find active task definition with name "{name}".')

    return response["taskDefinitionArns"][0].rsplit(":", 1)[0]


def _fetch_task(ecs, logs, cluster: str, task_arn: str):
    described_task = ecs.describe_tasks(cluster=cluster, tasks=[task_arn])["tasks"][0]

    task_definition = ecs.describe_task_definition(taskDefinition=described_task["taskDefinitionArn"])

    log_configuration = task_definition["taskDefinition"]["containerDefinitions"][0]["logConfiguration"]
    describe_log_streams = logs.describe_log_streams(
        logGroupName=log_configuration["options"]["awslogs-group"],
        orderBy="LastEventTime",
        descending=True,
        limit=1,
    )
    log_events = logs.get_log_events(
        logGroupName=log_configuration["options"]["awslogs-group"],
        logStreamName=describe_log_streams["logStreams"][0]["logStreamName"],
        limit=100,
        startFromHead=False,
    )

    return {"task": described_task, "task_definition": task_definition["taskDefinition"], "logs": log_events}


def fetch_task(context: ContextObject, click_params):
    return _fetch_task(context.ecs, context.logs, click_params["cluster"], _task_arn_helper(context, click_params))


def fetch_run_task(context: ContextObject, click_params):
    if not getattr(fetch_run_task, "task_ran", False):
        args = {"cluster": click_params["cluster"]}

        try:
            _, _ = click_params["task_definition"].split(":")
            args["taskDefinition"] = click_params["task_definition"]
        except ValueError:
            args["taskDefinition"] = _fetch_latest_active_task_definition(context.ecs, click_params["task_definition"])

        if click_params["command"]:
            args["overrides"] = {
                "containerOverrides": [
                    {"name": args["taskDefinition"].rsplit("/")[1], "command": click_params["command"]}
                ]
            }

        if click_params["capacity_provider_strategy"]:
            args["capacityProviderStrategy"] = [json.loads(click_params["capacity_provider_strategy"])]

        if click_params["network_configuration"]:
            args["networkConfiguration"] = json.loads(click_params["network_configuration"])

        result = context.ecs.run_task(**args)

        fetch_run_task.task_ran = True
        fetch_run_task.task_arn = result["tasks"][0]["taskArn"]

    return _fetch_task(context.ecs, context.logs, click_params["cluster"], fetch_run_task.task_arn)


def fetch_listing(context: ContextObject, click_params):
    return base_fetch_listing(
        context.ecs,
        paginator_type="list_tasks",
        arn_index="taskArns",
        describe_function=context.ecs.describe_tasks,
        describe_filter="tasks",
        result_key="tasks",
        paginator_params={"cluster": click_params["cluster"]},
    )


def fetch_logs(context: ContextObject, click_params):
    task_arn = _task_arn_helper(context, click_params)
    described_task = context.ecs.describe_tasks(cluster=click_params["cluster"], tasks=[task_arn])["tasks"][0]

    task_definition = context.ecs.describe_task_definition(taskDefinition=described_task["taskDefinitionArn"])

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
        limit=25,
        startFromHead=False,
    )

    return {"logs": log_events}
