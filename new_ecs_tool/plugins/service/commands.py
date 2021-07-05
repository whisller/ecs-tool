import click

from .data import fetch_service_dashboard
from .layouts import ServiceDashboardLayout
from ... import logger
from ...data_loader import DataLoader
from ...runner import Runner
from ...ui import Ui


@click.command(help="List available services")
def listing():
    logger.info(__name__)


@click.command(help="Dashboard")
@click.argument("service")
@click.option("--cluster", default="main")
@click.pass_context
def dashboard(ctx, **kwargs):
    ui = Ui(
        ServiceDashboardLayout, DataLoader(ctx.obj, kwargs, fetch_service_dashboard)
    )

    runner = Runner(ui)
    runner.run()
