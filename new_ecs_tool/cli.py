import click

from new_ecs_tool.context import ContextObject
from .plugins import cluster, dashboard, service, task


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = ContextObject()


cli.add_command(cluster.cli)
cli.add_command(dashboard.cli)
cli.add_command(service.cli)
cli.add_command(task.cli)


if __name__ == "__main__":
    cli()
