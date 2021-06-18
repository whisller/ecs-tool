from rich.panel import Panel
from rich.table import Table


class ServiceDashboardLayout:
    def __init__(self, base_layout):
        self.base_layout = base_layout
        self.data = None

    def header(self):
        from datetime import datetime
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        # grid.add_column(justify="right")

        grid.add_row(f"Clusters > {self.data['click_params']['cluster']} > Services > {self.data['fetcher']['services'][0]}")
        return Panel(grid, style="white on blue")

    def refresh(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())

        return self.base_layout
