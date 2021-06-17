import click

from .commands import cluster_list


@click.group(name="cluster")
@click.pass_context
def cli(ctx):
    """
    Cluster related commands
    """


cli.add_command(cluster_list)
