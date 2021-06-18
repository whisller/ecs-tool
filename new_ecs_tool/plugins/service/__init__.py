import click

from .commands import listing, dashboard


@click.group(name="service")
@click.pass_context
def cli(ctx):
    """
    Service related commands
    """


cli.add_command(listing)
cli.add_command(dashboard)
