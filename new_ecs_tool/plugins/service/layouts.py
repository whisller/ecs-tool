from enum import Enum, unique

import arrow
from rich.layout import Layout
from rich.table import Table
from new_ecs_tool.ui import AsciiPlotIntegration, EcsPanel, StatusEnum


@unique
class ServiceStatusEnum(Enum):
    ACTIVE = StatusEnum.ACTIVE.value
    DRAINING = StatusEnum.IN_PROGRESS.value
    INACTIVE = StatusEnum.STOPPED.value


class TaskLifecycleStatusEnum(Enum):
    RUNNING = StatusEnum.ACTIVE.value
    ACTIVATING = StatusEnum.IN_PROGRESS.value
    DEACTIVATING = StatusEnum.IN_PROGRESS.value
    PENDING = StatusEnum.IN_PROGRESS.value
    STOPPING = StatusEnum.IN_PROGRESS.value
    PROVISIONING = StatusEnum.IN_PROGRESS.value
    DEPROVISIONING = StatusEnum.IN_PROGRESS.value
    STOPPED = StatusEnum.STOPPED.value


class DashboardLayout:
    def __init__(self, base_layout):
        self.base_layout = base_layout
        self.data = None

    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"Clusters > {self.data.click_params['cluster']} > Services > {self.data.click_params['service']}",
            self.data.fetcher["services"]["ResponseMetadata"]["HTTPHeaders"]["date"],
        )
        return EcsPanel(grid)

    def basic_info(self):
        service = self.data.fetcher["services"]["services"][0]
        status = ServiceStatusEnum[service["status"]].value

        grid = Table.grid()
        grid.add_column()
        grid.add_column()
        grid.add_row(
            "Status: ",
            f"[{status.colour}]{status.icon}[/{status.colour}]  ({service['status'].lower()})",
        )
        grid.add_row("Type: ", f"{service['schedulingStrategy']}")
        grid.add_row("Launch: ", f"{service['launchType']}")
        grid.add_row(
            "Tasks: ",
            f"{service['runningCount']}/{service['desiredCount']} ({service['pendingCount']} pending)",
        )
        if "deployments" in service:
            deployment_primary = None
            deployment_active = None
            for deployment in service["deployments"]:
                if deployment["status"] == "PRIMARY":
                    deployment_primary = arrow.get(deployment["updatedAt"])

                if deployment["status"] == "ACTIVE":
                    deployment_active = arrow.get(deployment["createdAt"])

            if not deployment_active:
                deployment_status = f"Completed at {deployment_primary.format('YYYY-MM-DD HH:mm:ss ZZ')}"
            else:
                deployment_status = (
                    f"Running from {deployment_active.format('YYYY-MM-DD HH:mm:ss ZZ')}"
                )

            grid.add_row("Deployment: ", deployment_status)

        return EcsPanel(grid, title="Basic info")

    def tasks(self):
        grid = Table.grid()
        grid.add_column()
        grid.add_column()

        for task in self.data.fetcher["tasks"]["tasks"]:
            status = TaskLifecycleStatusEnum[task["lastStatus"]].value

            grid.add_row(
                task["taskArn"].split("/")[-1][:8] + "... ",
                f"[{status.colour}]{status.icon}[/{status.colour}]  ({task['lastStatus'].lower()})",
            )

        return EcsPanel(grid, title="Tasks")

    def memory(self):
        return EcsPanel(
            AsciiPlotIntegration(self.data.fetcher["cloudwatch_memory_data"]),
            title="MemoryUtilization",
        )

    def cpu(self):
        return EcsPanel(
            AsciiPlotIntegration(self.data.fetcher["cloudwatch_cpu_data"]),
            title="CPUUtilization",
        )

    def logs(self):
        data = self.data.fetcher["logs"]
        grid = Table.grid()
        grid.add_column()

        for event in data["events"]:
            grid.add_row(event["message"])

        return EcsPanel(grid, title="Last logs")

    def load(self, data):
        self.data = data
        self.base_layout["main"].split_row(
            Layout(name="main_left"),
            Layout(name="main_right", ratio=2, minimum_size=60),
        )
        self.base_layout["main_left"].split(
            Layout(name="main_left_basic_info"),
            Layout(name="main_left_tasks"),
        )
        self.base_layout["main_right"].split(
            Layout(name="main_right_top"),
            Layout(name="main_right_bottom"),
        )
        self.base_layout["main_right_top"].split(
            Layout(name="main_right_top_cpu"),
            Layout(name="main_right_top_memory"),
        )

        self.base_layout["header"].update(self.header())

        self.base_layout["main_left_basic_info"].update(self.basic_info())
        self.base_layout["main_left_tasks"].update(self.tasks())

        self.base_layout["main_right_top_memory"].update(self.memory())
        self.base_layout["main_right_top_cpu"].update(self.cpu())

        self.base_layout["main_right_bottom"].update(self.logs())

        return self.base_layout


class ListingLayout:
    def __init__(self, base_layout):
        self.base_layout = base_layout
        self.data = None

    def main(self):
        table = Table(title="Star Wars Movies")

        table.add_column("Released", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Box Office", justify="right", style="green")

        table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
        table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
        table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
        table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")

        return table

    def load(self, data):
        self.base_layout["main"].update(self.main())

        return self.base_layout
