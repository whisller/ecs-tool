from dataclasses import dataclass
from enum import Enum, unique

from asciiplot import asciiize
from rich.ansi import AnsiDecoder
from rich.console import RenderGroup
from rich.jupyter import JupyterMixin
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

NO_DATA_AVAILABLE = Text("No data available", style="bold red")


def make_layout():
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
    )

    return layout


class BaseLayout:
    def __init__(self, base_layout, params=None):
        self.base_layout = base_layout
        self.params = params
        self.data = None


class Ui:
    def __init__(self, base_layout, layout, data_loader, layout_params=None):
        self.base_layout = base_layout
        self.layout = layout
        self.layout_params = layout_params
        self.data_loader = data_loader

    def refresh(self):
        return self.layout(self.base_layout(), self.layout_params).load(self.data_loader.fetch_data())


class EcsPanel(Panel):
    def __init__(self, *args, **kwargs):
        kwargs["style"] = "white on black"
        super().__init__(*args, **kwargs)


class AsciiPlotIntegration(JupyterMixin):
    def __init__(self, data):
        y_values, x_ticks = self._prepare_data(data)
        chart = asciiize(y_values, inter_points_margin=4, x_ticks=x_ticks)

        decoder = AnsiDecoder()
        self.rich_chart = RenderGroup(*decoder.decode(chart))

    def __rich_console__(self, console, options):
        yield self.rich_chart

    def _prepare_data(self, data):
        x_labels = []
        y_values = []
        for record in data:
            x_labels.append(record["Timestamp"].strftime("%H:%M"))
            y_values.append(round(record["Average"], 2))

        x_ticks = [" "] * len(x_labels)
        half = int(len(x_labels) / 2)
        x_ticks[0] = x_labels[0]
        x_ticks[half] = x_labels[half]
        x_ticks[-1] = x_labels[-1]

        return y_values, x_ticks


@dataclass
class StatusStyle:
    colour: str
    icon: str


@unique
class StatusEnum(Enum):
    ACTIVE = StatusStyle("green", "\u2B24")
    IN_PROGRESS = StatusStyle("yellow", "\u25D6")
    STOPPED = StatusStyle("red", "\u25CB")


class TaskLifecycleStatusEnum(Enum):
    RUNNING = StatusEnum.ACTIVE.value
    ACTIVATING = StatusEnum.IN_PROGRESS.value
    DEACTIVATING = StatusEnum.IN_PROGRESS.value
    PENDING = StatusEnum.IN_PROGRESS.value
    STOPPING = StatusEnum.IN_PROGRESS.value
    PROVISIONING = StatusEnum.IN_PROGRESS.value
    DEPROVISIONING = StatusEnum.IN_PROGRESS.value
    STOPPED = StatusEnum.STOPPED.value
