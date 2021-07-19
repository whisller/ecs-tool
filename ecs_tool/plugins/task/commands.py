import click

from ... import logger


@click.command(help="Run task")
@click.option("--cluster", default="main")
@click.option("--wait", is_flag=True, help="Wait till task will reach STOPPED status.")
@click.option("--wait-delay", default=3, help="Delay between task status check.")
@click.option(
    "--wait-max-attempts",
    default=100,
    help="Maximum attempts to check if task finished.",
)
@click.argument("task-definition", required=True)
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, **kwargs):
    logger.info(__name__)
