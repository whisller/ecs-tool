import click

from .commands import task_list


@click.group(name="task")
@click.pass_context
def cli(ctx):
    """
    Task related commands
    """


cli.add_command(task_list)
