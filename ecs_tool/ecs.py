import itertools

import botocore

from ecs_tool.exceptions import (
    NoResultsException,
    TaskDefinitionInactiveException,
    WaiterException,
    NoTaskDefinitionFoundException,
    NotSupportedLogDriver,
    NoLogStreamsFound,
)
from ecs_tool.tables import (
    TasksTable,
    TaskLogTable,
    ServicesTable,
    TaskDefinitionsTable,
)


def _paginate(ecs_client, service, **kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    paginator = ecs_client.get_paginator(service)
    pagination_config = {"MaxItems": 100, "PageSize": 100}

    resp = paginator.paginate(**kwargs, PaginationConfig=pagination_config)
    yield resp

    while "NextToken" in resp:
        yield paginator.paginate(
            {
                **kwargs,
                **{"PaginationConfig": pagination_config},
                **{"StartingToken": resp["NextToken"]},
            }
        )


def fetch_services(ecs_client, cluster, launch_type=None, scheduling_strategy=None):
    pagination = _paginate(
        ecs_client,
        "list_services",
        cluster=cluster,
        launchType=launch_type,
        schedulingStrategy=scheduling_strategy,
    )

    arns = []
    try:
        for iterator in pagination:
            for service in iterator:
                arns += service["serviceArns"]
    except ecs_client.exceptions.ClusterNotFoundException:
        raise NoResultsException("No results found.")

    if not arns:
        raise NoResultsException("No results found.")

    describe_services = ecs_client.describe_services(cluster=cluster, services=arns)

    return ServicesTable.build(describe_services["services"])


def fetch_tasks(
    ecs_client, cluster, status, service_name=None, family=None, launch_type=None
):
    if status == "ANY":
        pagination_running = _paginate(
            ecs_client,
            "list_tasks",
            cluster=cluster,
            desiredStatus="RUNNING",
            serviceName=service_name,
            family=family,
            launchType=launch_type,
        )

        pagination_stopped = _paginate(
            ecs_client,
            "list_tasks",
            cluster=cluster,
            desiredStatus="STOPPED",
            serviceName=service_name,
            family=family,
            launchType=launch_type,
        )

        pagination = itertools.chain(pagination_running, pagination_stopped)
    else:
        pagination = _paginate(
            ecs_client,
            "list_tasks",
            cluster=cluster,
            desiredStatus=status,
            serviceName=service_name,
            family=family,
            launchType=launch_type,
        )

    arns = []
    for iterator in pagination:
        for task in iterator:
            arns += task["taskArns"]

    if not arns:
        raise NoResultsException("No results found.")

    describe_services = ecs_client.describe_tasks(cluster=cluster, tasks=arns)

    return TasksTable.build(describe_services["tasks"])


def fetch_task_definitions(ecs_client, family, status):
    pagination = _paginate(
        ecs_client, "list_task_definitions", familyPrefix=family, status=status
    )

    arns = []
    for iterator in pagination:
        for task_definition in iterator:
            arns += task_definition["taskDefinitionArns"]

    if not arns:
        raise NoResultsException("No results found.")

    return TaskDefinitionsTable.build(arns)


def task_logs(ecs_client, logs_client, cluster, task):
    tasks = ecs_client.describe_tasks(cluster=cluster, tasks=[task])

    if not tasks["tasks"]:
        raise NoResultsException("No results found.")

    task_definition = ecs_client.describe_task_definition(
        taskDefinition=tasks["tasks"][0]["taskDefinitionArn"]
    )

    log_configuration = task_definition["taskDefinition"]["containerDefinitions"][0][
        "logConfiguration"
    ]
    if log_configuration["logDriver"] != "awslogs":
        raise NotSupportedLogDriver(
            f'Log driver "{log_configuration["logDriver"]}" is not supported yet.'
        )

    describe_log_streams = logs_client.describe_log_streams(
        logGroupName=log_configuration["options"]["awslogs-group"],
        orderBy="LastEventTime",
        descending=True,
        limit=1,
    )

    if not describe_log_streams["logStreams"]:
        raise NoLogStreamsFound("No logs found.")

    log_events = logs_client.get_log_events(
        logGroupName=log_configuration["options"]["awslogs-group"],
        logStreamName=describe_log_streams["logStreams"][0]["logStreamName"],
        limit=100,
        startFromHead=True,
    )

    if not log_events["events"]:
        raise NoLogStreamsFound("No logs found.")

    return TaskLogTable.build(log_events["events"])


def run_ecs_task(
    ecs_client,
    logs_client,
    cluster,
    task_definition,
    wait,
    wait_delay,
    wait_max_attempts,
    logs,
    command=None,
):
    args = {"cluster": cluster}

    try:
        _, _ = task_definition.split(":")
        args["taskDefinition"] = task_definition
    except ValueError:
        args["taskDefinition"] = _fetch_latest_active_task_definition(
            ecs_client, task_definition
        )

    if command:
        args["overrides"] = {
            "containerOverrides": [
                {"name": task_definition.rsplit(":", 1)[0], "command": command}
            ]
        }

    try:
        result = ecs_client.run_task(**args)
    except ecs_client.exceptions.InvalidParameterException as e:
        raise TaskDefinitionInactiveException(e)

    describe_tasks = ecs_client.describe_tasks(
        cluster=cluster, tasks=(result["tasks"][0]["taskArn"],)
    )

    yield TasksTable.build(describe_tasks["tasks"])

    if wait:
        waiter = ecs_client.get_waiter("tasks_stopped")

        try:
            waiter.wait(
                cluster=cluster,
                tasks=(result["tasks"][0]["taskArn"],),
                WaiterConfig={"Delay": wait_delay, "MaxAttempts": wait_max_attempts},
            )
        except botocore.exceptions.WaiterError as e:
            raise WaiterException(e)

    describe_tasks = ecs_client.describe_tasks(
        cluster=cluster, tasks=(result["tasks"][0]["taskArn"],)
    )

    yield TasksTable.build(describe_tasks["tasks"])

    if logs:
        yield task_logs(ecs_client, logs_client, cluster, result["tasks"][0]["taskArn"])


def _fetch_latest_active_task_definition(ecs_client, name):
    response = ecs_client.list_task_definitions(
        familyPrefix=name, status="ACTIVE", sort="DESC", maxResults=1
    )

    if not response["taskDefinitionArns"]:
        raise NoTaskDefinitionFoundException(
            f'Unable to find active task definition for "{name}".'
        )

    return response["taskDefinitionArns"][0].rsplit(":", 1)[0]
