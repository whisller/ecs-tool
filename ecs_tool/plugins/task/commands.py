import click

from ... import logger


@click.command(help="List available tasks")
def task_list():
    logger.info(__name__)
