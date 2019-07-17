import sys

import boto3
import click
from botocore.exceptions import NoRegionError, NoCredentialsError
from click import UsageError

from ecs_tool.ecs import (
    fetch_services,
    fetch_tasks,
    fetch_task_definitions,
    run_ecs_task,
    task_logs,
)
from ecs_tool.exceptions import (
    NoResultsException,
    TaskDefinitionInactiveException,
    WaiterException,
    NoTaskDefinitionFoundException,
    NotSupportedLogDriver,
    NoLogStreamsFound,
)
from ecs_tool.tables import (
    ServicesTable,
    TasksTable,
    TaskDefinitionsTable,
    TaskLogTable,
)


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
        logs_client = boto3.client("logs")
    except (NoRegionError, NoCredentialsError) as e:
        raise UsageError(f"AWS Configuration: {e}")

    ctx.obj["ecs_client"] = ecs_client
    ctx.obj["logs_client"] = logs_client


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
    except NoResultsException:
        click.secho("No results found.", fg="red")
        sys.exit()

    print(ServicesTable.build(result).table)


@cli.command(cls=EcsClusterCommand)
@click.option(
    "--status",
    type=click.Choice(["RUNNING", "STOPPED", "ANY"]),
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
    except NoResultsException as e:
        click.secho(e, fg="red")
        sys.exit()

    print(TasksTable.build(result).table)


@cli.command(cls=EcsClusterCommand)
@click.argument("task", required=True)
@click.pass_context
def task_log(ctx, cluster, task):
    """
    Display awslogs for task.

    task: Task id.
    """

    try:
        result = task_logs(ctx.obj["ecs_client"], ctx.obj["logs_client"], cluster, task)
    except (NoResultsException, NotSupportedLogDriver, NoLogStreamsFound) as e:
        click.secho(e, fg="red")
        sys.exit()

    print(TaskLogTable.build(result).table)


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
    except NoResultsException as e:
        click.secho(e, fg="red")
        sys.exit()

    print(TaskDefinitionsTable.build(result).table)


@cli.command(cls=EcsClusterCommand)
@click.option("--wait", is_flag=True, help="Wait till task will reach STOPPED status.")
@click.option("--wait-delay", default=3, help="Delay between task status check.")
@click.option(
    "--wait-max-attempts",
    default=100,
    help="Maximum attempts to check if task finished.",
)
@click.argument("task-definition", required=True)
@click.argument("command", nargs=-1)
@click.pass_context
def run_task(
    ctx, cluster, wait, wait_delay, wait_max_attempts, task_definition, command=None
):
    """
    Run task.

    task_definition: Task definition.\n
    command: Command passed to task. Needs to be passed after "--" e.g. ecs run-task my_definition:1 -- my_script/
    """
    try:
        results = run_ecs_task(
            ctx.obj["ecs_client"],
            cluster,
            task_definition,
            wait,
            wait_delay,
            wait_max_attempts,
            command,
        )

        for result in results:
            click.clear()
            print(TasksTable.build(result).table)

    except (
        TaskDefinitionInactiveException,
        WaiterException,
        NoTaskDefinitionFoundException,
    ) as e:
        click.secho(str(e), fg="red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
