import click

from .commands import service_list


@click.group(name="service")
@click.pass_context
def cli(ctx):
    """
    Service related commands
    """


cli.add_command(service_list)
