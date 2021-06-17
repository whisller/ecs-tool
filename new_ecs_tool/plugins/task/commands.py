import click

from new_ecs_tool import logger


@click.command(help="List available tasks")
def task_list():
    logger.info(__name__)
