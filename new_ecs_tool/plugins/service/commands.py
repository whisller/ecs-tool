import click

from .data import fetch_dashboard, fetch_listing
from .layouts import DashboardLayout, ListingLayout
from ...data_loader import DataLoader
from ...runner import LiveRunner, Runner
from ...ui import Ui, make_layout, make_dashboard_layout


@click.command(help="List available services")
@click.option("--cluster", default="main")
@click.pass_context
def listing(ctx, **kwargs):
    Runner(
        Ui(make_layout, ListingLayout, DataLoader(ctx.obj, kwargs, fetch_listing))
    ).run()


@click.command(help="Dashboard")
@click.argument("service")
@click.option("--cluster", default="main")
@click.pass_context
def dashboard(ctx, **kwargs):
    LiveRunner(
        Ui(
            make_dashboard_layout,
            DashboardLayout,
            DataLoader(ctx.obj, kwargs, fetch_dashboard),
        )
    ).run()
