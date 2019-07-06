import sys
import time
from datetime import datetime
from textwrap import wrap

import boto3
import click
from botocore.exceptions import NoRegionError, NoCredentialsError
from click import UsageError
from colorclass import Color
from terminaltables import SingleTable

from ecs_tool.exceptions import WaitParameterException

SERVICE_STATUS_COLOUR = {
    "ACTIVE": "autogreen",
    "DRAINING": "autoyellow",
    "INACTIVE": "autored",
}

TASK_STATUS_COLOUR = {
    "PROVISIONING": "autoblue",
    "PENDING": "automagenta",
    "ACTIVATING": "autoyellow",
    "RUNNING": "autogreen",
    "DEACTIVATING": "autoyellow",
    "STOPPING": "automagenta",
    "DEPROVISIONING": "autoblue",
    "STOPPED": "autored",
}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class EcsClusterCommand(click.core.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.insert(
            0,
            click.core.Option(
                ("--cluster",),
                default="default",
                help="Cluster name or ARN.",
                show_default=True,
            ),
        )


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}

    try:
        ecs_client = boto3.client("ecs")
    except (NoRegionError, NoCredentialsError) as e:
        raise UsageError(f"AWS Configuration: {e}")

    ctx.obj["ecs_client"] = ecs_client


@cli.command(cls=EcsClusterCommand)
@click.option(
    "--launch-type", type=click.Choice(["EC2", "FARGATE"]), help="Launch type"
)
@click.option(
    "--scheduling-strategy",
    type=click.Choice(["REPLICA", "DAEMON"]),
    help="Scheduling strategy",
)
@click.pass_context
def services(ctx, cluster, launch_type=None, scheduling_strategy=None):
    """
    List of services.

    D - Desired count
    P - Pending count
    R - Running count
    """

    table_data = [
        (
            "Service name",
            "Task definition",
            "Status",
            "D",
            "P",
            "R",
            "Service type",
            "Launch type",
        )
    ]

    args = {"cluster": cluster}

    if launch_type:
        args["launchType"] = launch_type

    if scheduling_strategy:
        args["schedulingStrategy"] = scheduling_strategy

    list_services = ctx.obj["ecs_client"].list_services(**args)
    if not list_services["serviceArns"]:
        click.secho("No results found.", fg="red")
        sys.exit()

    describe_services = ecs_client.describe_services(
        cluster=cluster, services=list_services["serviceArns"]
    )

    for service in describe_services["services"]:
        status_colour = SERVICE_STATUS_COLOUR.get(service["status"])

        table_data.append(
            [
                service["serviceName"],
                service["taskDefinition"].rsplit("task-definition/", 1)[-1],
                Color(f"{{{status_colour}}}{service['status']}{{/{status_colour}}}"),
                service["desiredCount"],
                service["pendingCount"],
                service["runningCount"],
                service["schedulingStrategy"],
                service["launchType"],
            ]
        )

    table = SingleTable(table_data)
    table.inner_row_border = True
    print(table.table)


@cli.command(cls=EcsClusterCommand)
@click.option(
    "--status",
    type=click.Choice(["RUNNING", "STOPPED"]),
    default="RUNNING",
    help="Task status",
    show_default=True,
)
@click.option("--service-name", help="Service name")
@click.option("--family", help="Family name")
@click.option(
    "--launch-type", type=click.Choice(["EC2", "FARGATE"]), help="Launch type"
)
@click.pass_context
def tasks(ctx, cluster, status, service_name=None, family=None, launch_type=None):
    """
    List of tasks.
    """

    table_data = [
        (
            "Task",
            "Task definition",
            "Status",
            "Command",
            "Started at",
            "Stopped at",
            "Execution time",
            "Exit code",
            "Exit reason",
            "Stopped reason",
        )
    ]

    args = {"cluster": cluster}

    if service_name:
        args["serviceName"] = service_name

    if family:
        args["family"] = family

    if status:
        args["desiredStatus"] = status

    if launch_type:
        args["launchType"] = launch_type

    list_tasks = ctx.obj["ecs_client"].list_tasks(**args)
    if not list_tasks["taskArns"]:
        click.secho("No results found.", fg="red")
        sys.exit()

    describe_tasks = ctx.obj["ecs_client"].describe_tasks(
        cluster=cluster, tasks=list_tasks["taskArns"]
    )

    for task in describe_tasks["tasks"]:
        status_colour = TASK_STATUS_COLOUR.get(task["lastStatus"])

        table_data.append(
            [
                task["taskArn"].rsplit("task/", 1)[-1],
                task["taskDefinitionArn"].rsplit("task-definition/", 1)[-1],
                Color(f"{{{status_colour}}}{task['lastStatus']}{{/{status_colour}}}"),
                " ".join(task["overrides"]["containerOverrides"][0].get("command", "")),
                task.get("startedAt").strftime(DATE_FORMAT)
                if task.get("startedAt")
                else "",
                task.get("stoppedAt").strftime(DATE_FORMAT)
                if task.get("stoppedAt")
                else "",
                task.get("stoppedAt") - task.get("startedAt")
                if all((task.get("startedAt"), task.get("stoppedAt")))
                else "",
                task.get("containers")[0].get("exitCode")
                if task.get("containers")[0].get("exitCode")
                else "",
                _wrap(task.get("containers")[0].get("reason"), 10),
                _wrap(task.get("stoppedReason"), 10),
            ]
        )

    table = SingleTable(table_data)
    table.inner_row_border = True
    print(table.table)


@cli.command()
@click.option("--family", help="Family name")
@click.option("--status", type=click.Choice(["ACTIVE", "INACTIVE"]), help="Status")
@click.pass_context
def task_definitions(ctx, family=None, status=None):
    """
    List of task definitions.
    """

    args = {}

    if family:
        args["familyPrefix"] = family

    if status:
        args["status"] = status

    table_data = [("Task definition",)]

    response = ctx.obj["ecs_client"].list_task_definitions(**args)
    for definition in response["taskDefinitionArns"]:
        table_data.append([definition.rsplit("task-definition/", 1)[-1]])

    table = SingleTable(table_data)
    table.inner_row_border = True
    print(table.table)


@cli.command(cls=EcsClusterCommand)
@click.option("--wait", is_flag=True, help="Wait till task will reach STOPPED status.")
@click.argument("task-definition", required=True)
@click.argument("command", nargs=-1)
@click.pass_context
def run_task(ctx, cluster, task_definition, wait, command=None):
    """
    Run task.

    task_definition: Task definition.\n
    command: Command passed to task. Needs to be passed after "--" e.g. ecs run-task my_definition:1 -- my_script/
    """
    started_by = "ecs-tool:" + str(datetime.timestamp(datetime.now()))

    args = {
        "cluster": cluster,
        "taskDefinition": task_definition,
        "startedBy": started_by,
    }

    if command:
        args["overrides"] = {
            "containerOverrides": [
                {"name": task_definition.rsplit(":", 1)[0], "command": command}
            ]
        }

    response = ctx.obj["ecs_client"].run_task(**args)

    if not wait:
        click.echo(f"Task ARN: {response['tasks'][0]['taskArn']}")
        sys.exit(0)

    list_tasks_args = {
        "cluster": cluster,
        "startedBy": started_by,
        "desiredStatus": "STOPPED",
    }

    while True:
        list_tasks = ctx.obj["ecs_client"].list_tasks(**list_tasks_args)
        if list_tasks["taskArns"]:
            describe_tasks = ctx.obj["ecs_client"].describe_tasks(
                cluster=cluster, tasks=list_tasks["taskArns"]
            )
            if len(describe_tasks["tasks"]) > 1:
                raise WaitParameterException

            task = describe_tasks["tasks"][0]
            break

        time.sleep(2)

    table_data = [
        (
            "Task",
            "Task definition",
            "Status",
            "Command",
            "Started at",
            "Stopped at",
            "Execution time",
            "Exit code",
            "Exit reason",
            "Stopped reason",
        )
    ]

    status_colour = TASK_STATUS_COLOUR.get(task["lastStatus"])

    table_data.append(
        [
            task["taskArn"].rsplit("task/", 1)[-1],
            task["taskDefinitionArn"].rsplit("task-definition/", 1)[-1],
            Color(f"{{{status_colour}}}{task['lastStatus']}{{/{status_colour}}}"),
            " ".join(task["overrides"]["containerOverrides"][0].get("command", "")),
            task.get("startedAt").strftime(DATE_FORMAT)
            if task.get("startedAt")
            else "",
            task.get("stoppedAt").strftime(DATE_FORMAT)
            if task.get("stoppedAt")
            else "",
            task.get("stoppedAt") - task.get("startedAt")
            if all((task.get("startedAt"), task.get("stoppedAt")))
            else "",
            task.get("containers")[0].get("exitCode")
            if task.get("containers")[0].get("exitCode")
            else "",
            _wrap(task.get("containers")[0].get("reason"), 10),
            _wrap(task.get("stoppedReason"), 10),
        ]
    )

    table = SingleTable(table_data)
    table.inner_row_border = True
    print(table.table)


if __name__ == "__main__":
    cli()


def _wrap(text, size):
    if not text:
        return ""

    return "\n".join(wrap(text, size)) + "\n"
