import click
from rich.console import Console

from .context import ContextObject
from .exception import EcsToolException
from .plugins import cluster, service, task


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = ContextObject()


def safe_cli():
    """
    Used as an entry point in pyproject.toml::tool.poetry.scripts
    To handle global exceptions.
    """
    console = Console()
    try:
        cli()
    except EcsToolException as e:
        console.print(e.message, style="bold red")
        return
    except Exception as e:
        if type(e).__qualname__ == "ClusterNotFoundException":
            # Handle botocore.errorfactory.ClusterNotFoundException exception
            console.print(
                "Cluster not found. To list available clusters run: ecs cluster list",
                style="bold red",
            )
            return
        if type(e).__qualname__ == "ServiceNotFoundException":
            # handle botocore.errorfactory.ServiceNotFoundException
            console.print(
                "Service not found in this cluster. To list available services run: ecs service list",
                style="bold red",
            )
            return

        raise


cli.add_command(cluster.cli)
cli.add_command(service.cli)
cli.add_command(task.cli)


if __name__ == "__main__":
    cli()
