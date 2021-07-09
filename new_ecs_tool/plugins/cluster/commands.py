import click

from new_ecs_tool.data_loader import DataLoader
from new_ecs_tool.plugins.cluster.data import fetch_listing
from new_ecs_tool.plugins.cluster.layouts import ListingLayout
from new_ecs_tool.runner import Runner
from new_ecs_tool.ui import Ui, make_layout


@click.command(help="List available clusters", name="list")
@click.pass_context
def listing(ctx):
    Runner(Ui(make_layout, ListingLayout, DataLoader(ctx.obj, fetch_listing))).run()
