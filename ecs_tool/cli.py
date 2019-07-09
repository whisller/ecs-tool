import sys
import time
from datetime import datetime

import boto3
import click
from botocore.exceptions import NoRegionError, NoCredentialsError
from click import UsageError

from ecs_tool.ecs import fetch_services, fetch_tasks, fetch_task_definitions
from ecs_tool.exceptions import WaitParameterException, NoResultsException
from ecs_tool.tables import ServicesTable, TasksTable, TaskDefinitionsTable


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

    try:
        result = fetch_services(
            ctx.obj["ecs_client"], cluster, launch_type, scheduling_strategy
        )
        print(ServicesTable.build(result).table)
    except NoResultsException:
        click.secho("No results found.", fg="red")
        sys.exit()


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

    try:
        result = fetch_tasks(
            ctx.obj["ecs_client"], cluster, status, service_name, family, launch_type
        )
        print(TasksTable.build(result).table)
    except NoResultsException:
        click.secho("No results found.", fg="red")
        sys.exit()


@cli.command()
@click.option("--family", help="Family name")
@click.option("--status", type=click.Choice(["ACTIVE", "INACTIVE"]), help="Status")
@click.pass_context
def task_definitions(ctx, family=None, status=None):
    """
    List of task definitions.
    """

    try:
        result = fetch_task_definitions(ctx.obj["ecs_client"], family, status)
        print(TaskDefinitionsTable.build(result).table)
    except NoResultsException:
        click.secho("No results found.", fg="red")
        sys.exit()


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

    ctx.obj["ecs_client"].run_task(**args)

    if wait:
        while True:
            list_tasks = ctx.obj["ecs_client"].list_tasks(
                cluster=cluster, startedBy=started_by, desiredStatus="STOPPED"
            )
            if list_tasks["taskArns"]:
                describe_tasks = ctx.obj["ecs_client"].describe_tasks(
                    cluster=cluster, tasks=list_tasks["taskArns"]
                )
                if len(describe_tasks["tasks"]) > 1:
                    raise WaitParameterException

                tasks = describe_tasks["tasks"]
                break

            time.sleep(2)

        print(TasksTable.build(tasks).table)
    else:
        list_tasks = ctx.obj["ecs_client"].list_tasks(
            cluster=cluster, startedBy=started_by
        )
        describe_tasks = ctx.obj["ecs_client"].describe_tasks(
            cluster=cluster, tasks=list_tasks["taskArns"]
        )

        print(TasksTable.build(describe_tasks["tasks"]).table)


if __name__ == "__main__":
    cli()
