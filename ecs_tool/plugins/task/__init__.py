import click

from .commands import run


@click.group(name="task")
@click.pass_context
def cli(ctx):
    """
    Task [run]
    """


cli.add_command(run)
