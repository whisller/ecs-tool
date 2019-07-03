import boto3
import click
from colorclass import Color
from terminaltables import SingleTable

SERVICE_STATUS_TO_COLOUR = {
    "ACTIVE": "autogreen",
    "DRAINING": "autoyellow",
    "INACTIVE": "autored",
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
    describe_services = client.describe_services(
        cluster=cluster, services=list_services["serviceArns"]
    )

    for service in describe_services["services"]:
        status_colour = SERVICE_STATUS_TO_COLOUR.get(service["status"])

        table_data.append(
            [
                service["serviceName"],
                _task_definition_name(service["taskDefinition"]),
                Color(f"{{{status_colour}}}{service['status']}{{/{status_colour}}}"),
                service["desiredCount"],
                service["pendingCount"],
                service["runningCount"],
                service["schedulingStrategy"],
                service["launchType"],
            ]
        )

    table = SingleTable(table_data)
    print(table.table)


if __name__ == "__main__":
    cli()


def _task_definition_name(taskDefinitionArn):
    return taskDefinitionArn.rsplit("task-definition/", 1)[-1]
