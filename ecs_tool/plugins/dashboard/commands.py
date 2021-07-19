import click

from ... import logger


@click.command(help="Starts dashboard")
def dashboard_start():
    logger.info(__name__)
