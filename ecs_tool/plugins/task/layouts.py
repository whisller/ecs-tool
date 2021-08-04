import arrow
from rich.layout import Layout
from rich.table import Table

from ... import DATE_FORMAT
from ...ui import BaseLayout, EcsPanel, TaskLifecycleStatusEnum


class TaskLayout(BaseLayout):
    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        title = f"Clusters > {self.data.click_params['cluster']} > {self.params['header_title']} > {self.data.fetcher['task_definition']['taskDefinitionArn'].rsplit('/')[1]} > {self.data.fetcher['task']['taskArn'].rsplit('/')[2]}"
        grid.add_row(title)

        return EcsPanel(grid)

    def main_left(self):
        grid = Table.grid()
        grid.add_column()
        grid.add_column()

        status = TaskLifecycleStatusEnum[self.data.fetcher["task"]["lastStatus"]].value

        grid.add_row(
            "Status: ",
            f"[{status.colour}]{status.icon}[/{status.colour}]  ({self.data.fetcher['task']['lastStatus'].lower()})",
        )
        grid.add_row(
            "Definition: ",
            self.data.fetcher["task"]["taskDefinitionArn"].rsplit("/")[1],
        )
        if self.data.fetcher["task"].get("startedAt"):
            label = "Started At: "
            key = "startedAt"
        else:
            label = "Created At: "
            key = "createdAt"
        grid.add_row(
            label,
            arrow.get(self.data.fetcher["task"][key]).format(DATE_FORMAT),
        )
        grid.add_row("Memory: ", self.data.fetcher["task"]["memory"])
        grid.add_row("CPU: ", self.data.fetcher["task"]["cpu"])

        return EcsPanel(grid, title="Basic info")

    def main_right(self):
        grid = Table.grid()
        grid.add_column()

        for event in self.data.fetcher["logs"]["events"]:
            grid.add_row(event["message"])

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
