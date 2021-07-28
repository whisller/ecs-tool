import click

from ...data_loader import DataLoader
from ...runner import LiveRunner, Runner
from ...ui import Ui, make_layout
from .data import fetch_dashboard, fetch_listing
from .layouts import DashboardLayout, ListingLayout


@click.command(help="List available services", name="list")
@click.option("--cluster", default="main")
@click.pass_context
def listing(ctx, **kwargs):
    Runner(Ui(make_layout, ListingLayout, DataLoader(ctx.obj, fetch_listing, kwargs))).run()


@click.command(help="Dashboard of service")
@click.argument("service")
@click.option("--cluster", default="main")
@click.pass_context
def dashboard(ctx, **kwargs):
    LiveRunner(
        Ui(
            make_layout,
            DashboardLayout,
            DataLoader(ctx.obj, fetch_dashboard, kwargs),
        )
    ).run()
