import click

from .commands import dashboard_start


@click.group(name="dashboard")
@click.pass_context
def cli(ctx):
    """
    Starts dashboard
    """


cli.add_command(dashboard_start)
