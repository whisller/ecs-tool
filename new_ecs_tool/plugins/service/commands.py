import click

from new_ecs_tool import logger


@click.command(help="List available services")
def service_list():
    logger.info(__name__)
