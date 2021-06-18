import click

from new_ecs_tool import logger


@click.command(help="Starts dashboard")
def dashboard_start():
    logger.info(__name__)
