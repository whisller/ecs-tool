from dataclasses import dataclass
from enum import Enum, unique

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table


@dataclass
class StatusStyle:
    colour: str
    icon: str


@unique
class StatusEnum(Enum):
    ACTIVE = StatusStyle("green", "\u2B24")
    DRAINING = StatusStyle("yellow", "\u25D6")
    INACTIVE = StatusStyle("red", "\u25CB")


class ServiceDashboardLayout:
    def __init__(self, base_layout):
        self.base_layout = base_layout
        self.data = None

    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"Clusters > {self.data.click_params['cluster']} > Services > {self.data.click_params['service']}",
            self.data.fetcher["services"]["ResponseMetadata"]["HTTPHeaders"]["date"]
        )
        return Panel(grid, style="white on blue")

    def basic_info(self):
        service = self.data.fetcher["services"]["services"][0]
        active = StatusEnum[service["status"]].value

        grid = Table.grid()
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Status: ",
            f"[{active.colour}]{active.icon}[/{active.colour}]  ({service['status'].lower()})"
        )
        grid.add_row("Type: ", f"{service['schedulingStrategy']}")
        grid.add_row("Launch: ", f"{service['launchType']}")
        grid.add_row(
            "Tasks: ",
            f"{service['runningCount']}/{service['desiredCount']} ({service['pendingCount']} pending)"
        )
        if "deployments" in service:
            deployment_primary = None
            deployment_active = None
            for deployment in service["deployments"]:
                if deployment["status"] == "PRIMARY":
                    deployment_primary = deployment

                if deployment["status"] == "ACTIVE":
                    deployment_active = deployment

            if not deployment_active:
                deployment_status = f"Completed (at {deployment_primary['updatedAt']})"
            else:
                deployment_status = f"Running (from {deployment_primary['createdAt']})"

            grid.add_row("Deployment: ", deployment_status)

        return Panel(grid, title="Basic info", style="white on blue")

    # def tasks(self):
    #     grid = Table.grid()
    #     grid.add_column()
    #
    #     for task in self.data.fetcher["tasks"]["tasks"]:
    #         grid.add_row()
    #
    #     return Panel(grid, title="Tasks", style="white on blue")

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())

        self.base_layout["main"].split_row(
            Layout(name="main_left"),
            Layout(name="body", ratio=2, minimum_size=60),
        )
        self.base_layout["main_left"].split(
            Layout(name="basic_info"),
            Layout(name="tasks"),
        )
        self.base_layout["basic_info"].update(self.basic_info())
        # self.base_layout["tasks"].update(self.tasks())

        return self.base_layout
