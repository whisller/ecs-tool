import click

from .commands import listing


@click.group(name="cluster")
def cli():
    """
    Cluster related commands
    """


cli.add_command(listing)
