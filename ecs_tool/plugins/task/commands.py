import click

from ...data_loader import DataLoader
from ...runner import LiveRunner, Runner
from ...ui import Ui, make_layout
from .data import fetch_listing, fetch_logs, fetch_run_task, fetch_task
from .layouts import ListingLayout, LogsLayout, TaskLayout


@click.command(help="Run task")
@click.option("--cluster", default="main", type=str)
@click.option("--network-configuration", required=False, type=str)
@click.option("--capacity-provider-strategy", required=False, type=str)
@click.argument("task-definition", required=True, type=str)
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, **kwargs):
    LiveRunner(
        Ui(make_layout, TaskLayout, DataLoader(ctx.obj, fetch_run_task, kwargs), {"header_title": "Task > Run"})
    ).run()


@click.command(help="Show information about ran/running task")
@click.option("--cluster", default="main", type=str)
@click.argument("task-id", required=True, type=str)
@click.pass_context
def show(ctx, **kwargs):
    LiveRunner(Ui(make_layout, TaskLayout, DataLoader(ctx.obj, fetch_task, kwargs), {"header_title": "Task"})).run()


@click.command(help="List of running tasks", name="list")
@click.option("--cluster", default="main", type=str)
@click.pass_context
def listing(ctx, **kwargs):
    Runner(Ui(make_layout, ListingLayout, DataLoader(ctx.obj, fetch_listing, kwargs))).run()


@click.command(help="Show logs for task")
@click.option("--cluster", default="main", type=str)
@click.argument("task-id", required=True, type=str)
@click.pass_context
def logs(ctx, **kwargs):
    LiveRunner(Ui(make_layout, LogsLayout, DataLoader(ctx.obj, fetch_logs, kwargs))).run()
