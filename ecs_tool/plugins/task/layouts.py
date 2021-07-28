import arrow
from rich.layout import Layout
from rich.table import Table

from ecs_tool import DATE_FORMAT
from ecs_tool.ui import EcsPanel


class RunLayout:
    def __init__(self, base_layout):
        self.base_layout = base_layout
        self.data = None

    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")

        title = f"Clusters > {self.data.click_params['cluster']} > Task > Run > {self.data.click_params['task_definition']} > {self.data.fetcher['task']['taskArn'].rsplit('/')[2]}"
        grid.add_row(title)

        return EcsPanel(grid)

    def main_left(self):
        grid = Table.grid()
        grid.add_column()
        grid.add_column()

        grid.add_row(
            "Definition: ",
            self.data.fetcher["task"]["taskDefinitionArn"].rsplit("/")[1],
        )
        grid.add_row(
            "Started at: ",
            arrow.get(self.data.fetcher["task"]["startedAt"]).format(DATE_FORMAT),
        )
        grid.add_row("Memory: ", self.data.fetcher["task"]["memory"])
        grid.add_row("CPU: ", self.data.fetcher["task"]["cpu"])

        return EcsPanel(grid, title="Basic info")

    def main_right(self):
        grid = Table.grid()
        grid.add_column()

        return EcsPanel(grid, title="Last logs")

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())

        self.base_layout["main"].split_row(
            Layout(name="main_left"),
            Layout(name="main_right", ratio=2, minimum_size=60),
        )

        self.base_layout["main_left"].update(self.main_left())
        self.base_layout["main_right"].update(self.main_right())

        return self.base_layout
