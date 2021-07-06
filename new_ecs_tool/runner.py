from time import sleep

from rich.console import Console
from rich.live import Live


class Runner:
    def __init__(self, ui):
        self.ui = ui

    def run(self):
        console = Console()
        console.print(self.ui.refresh())


class LiveRunner:
    def __init__(self, ui):
        self.ui = ui

    def until(self, call=lambda: True):
        return call

    def run(self):
        with Live(self.ui.refresh(), refresh_per_second=0.1) as live:
            while self.until():
                sleep(0.1)
                live.update(self.ui.refresh())
