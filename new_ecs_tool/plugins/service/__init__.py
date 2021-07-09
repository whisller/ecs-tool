import click

from .commands import listing, dashboard


@click.group(name="service")
def cli():
    """
    Service related commands
    """


cli.add_command(listing)
cli.add_command(dashboard)
