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
        grid.add_row(
            "Created at: ",
            arrow.get(self.data.fetcher["task"]["createdAt"]).format(DATE_FORMAT)
            if self.data.fetcher["task"].get("createdAt")
            else None,
        )
        grid.add_row(
            "Started at: ",
            arrow.get(self.data.fetcher["task"]["startedAt"]).format(DATE_FORMAT)
            if self.data.fetcher["task"].get("startedAt")
            else None,
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


class ListingLayout(BaseLayout):
    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_row(f"Clusters > {self.data.click_params['cluster']} > Tasks")

        return EcsPanel(grid)

    def main(self):
        table = Table()

        table.add_column("ID")
        table.add_column("Definition")
        table.add_column("Status")
        table.add_column("Created at")
        table.add_column("Memory/CPU")

        for task in self.data.fetcher:
            status = TaskLifecycleStatusEnum[task["lastStatus"]].value
            table.add_row(
                task["taskArn"].rsplit("/")[-1],
                task["taskDefinitionArn"].rsplit("/")[-1],
                f"[{status.colour}]{status.icon}[/{status.colour}]",
                arrow.get(task["createdAt"]).format(DATE_FORMAT) if task.get("createdAt") else "",
                task["memory"] + "/" + task["cpu"],
            )

        return table

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())
        self.base_layout["main"].update(self.main())

        return self.base_layout


class LogsLayout(BaseLayout):
    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_row(f"Clusters > {self.data.click_params['cluster']} > Tasks > {self.data.click_params['task_id']}")

        return EcsPanel(grid)

    def main(self):
        table = Table()
        table.add_column("Time")
        table.add_column("Message")

        for event in self.data.fetcher["logs"]["events"]:
            table.add_row(arrow.get(event["timestamp"]).format(DATE_FORMAT), event["message"])

        return table

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())
        self.base_layout["main"].update(self.main())

        return self.base_layout
