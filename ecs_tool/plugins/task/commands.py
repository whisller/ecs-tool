import click

from .data import fetch_run_task
from .layouts import RunLayout
from ...data_loader import DataLoader
from ...runner import LiveRunner
from ...ui import Ui, make_layout


@click.command(help="Run task")
@click.option("--cluster", default="main")
@click.argument("task-definition", required=True)
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, **kwargs):
    LiveRunner(
        Ui(
            make_layout,
            RunLayout,
            DataLoader(ctx.obj, fetch_run_task, kwargs),
        )
    ).run()
