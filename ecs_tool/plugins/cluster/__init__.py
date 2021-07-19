import click

from .commands import listing


@click.group(name="cluster")
def cli():
    """
    Cluster [listing]
    """


cli.add_command(listing)
