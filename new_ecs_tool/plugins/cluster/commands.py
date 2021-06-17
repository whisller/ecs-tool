import click

from new_ecs_tool import logger


@click.command(help="List available clusters")
def cluster_list():
    logger.info(__name__)
