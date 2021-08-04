import click

from .commands import run, show


@click.group(name="task")
@click.pass_context
def cli(ctx):
    """
    Task [run, show]
    """


cli.add_command(run)
cli.add_command(show)
