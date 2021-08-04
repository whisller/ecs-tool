import click

from .commands import listing, logs, run, show


@click.group(name="task")
@click.pass_context
def cli(ctx):
    """
    Task [listing, show, run, logs]
    """


cli.add_command(listing)
cli.add_command(show)
cli.add_command(run)
cli.add_command(logs)
