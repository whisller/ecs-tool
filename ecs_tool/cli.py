import sys
from textwrap import wrap

import boto3
import click
from colorclass import Color
from terminaltables import SingleTable

SERVICE_STATUS_TO_COLOUR = {
    "ACTIVE": "autogreen",
    "DRAINING": "autoyellow",
    "INACTIVE": "autored",
}

TASK_STATUS_TO_COLOUR = {
    "PROVISIONING": "autoblue",
    "PENDING": "automagenta",
    "ACTIVATING": "autoyellow",
    "RUNNING": "autogreen",
    "DEACTIVATING": "autoyellow",
    "STOPPING": "automagenta",
    "DEPROVISIONING": "autoblue",
    "STOPPED": "autored"
}


@click.group()
def cli():
    pass


@cli.command()
@click.option("--cluster", default="default", help="Cluster name or ARN.")
def services(cluster):
    """
    Get list of services.

    D - Desired count
    P - Pending count
    R - Running count
    """

    client = boto3.client("ecs")

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

    list_services = client.list_services(cluster=cluster)
    if not list_services["serviceArns"]:
        click.echo("No results found.")
        sys.exit()

    describe_services = client.describe_services(
        cluster=cluster, services=list_services["serviceArns"]
    )

    for service in describe_services["services"]:
        status_colour = SERVICE_STATUS_TO_COLOUR.get(service["status"])

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


@cli.command()
@click.option("--cluster", default="default", help="Cluster name or ARN.")
@click.option("--service-name", help="Service name")
@click.option("--status", type=click.Choice(["RUNNING", "STOPPED"]), help="Task status")
@click.option("--launch-type", type=click.Choice(["EC2", "FARGATE"]), help="Launch type")
def tasks(cluster, service_name=None, status=None, launch_type=None):
    """
    Get list of tasks.
    """

    client = boto3.client("ecs")

    table_data = [
        ("Task", "Task definition", "Status", "Started at", "Stopped at", "Exit code", "Exit reason", "Stopped reason")
    ]

    args = {
        "cluster": cluster
    }

    if service_name:
        args["serviceName"] = service_name

    if status:
        args["desiredStatus"] = status

    if launch_type:
        args["launchType"] = launch_type

    list_tasks = client.list_tasks(**args)
    if not list_tasks["taskArns"]:
        click.echo("No results found.")
        sys.exit()

    describe_tasks = client.describe_tasks(cluster=cluster, tasks=list_tasks["taskArns"])
    for task in describe_tasks["tasks"]:
        status_colour = TASK_STATUS_TO_COLOUR.get(task["lastStatus"])

        table_data.append(
            [
                task["taskArn"].rsplit("task/", 1)[-1],
                task["taskDefinitionArn"].rsplit("task-definition/", 1)[-1],
                Color(f"{{{status_colour}}}{task['lastStatus']}{{/{status_colour}}}"),
                task.get("startedAt"),
                task.get("stoppedAt"),
                task.get("containers")[0].get("exitCode"),
                _wrap(task.get("containers")[0].get("reason"), 10),
                _wrap(task.get("stoppedReason"), 10)
            ]
        )

    table = SingleTable(table_data)
    table.inner_row_border = True
    print(table.table)


if __name__ == "__main__":
    cli()


def _wrap(text, size):
    if not text:
        return

    return "\n".join(wrap(text, size))+"\n"
