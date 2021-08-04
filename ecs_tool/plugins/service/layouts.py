from enum import Enum, unique

import arrow
from rich.layout import Layout
from rich.table import Table

from ... import DATE_FORMAT
from ...ui import NO_DATA_AVAILABLE, AsciiPlotIntegration, BaseLayout, EcsPanel, StatusEnum, TaskLifecycleStatusEnum


@unique
class ServiceStatusEnum(Enum):
    ACTIVE = StatusEnum.ACTIVE.value
    DRAINING = StatusEnum.IN_PROGRESS.value
    INACTIVE = StatusEnum.STOPPED.value


class DashboardLayout(BaseLayout):
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
                deployment_status = f"Completed at {deployment_primary.format(DATE_FORMAT)}"
            else:
                deployment_status = f"Running from {deployment_active.format(DATE_FORMAT)}"

            grid.add_row("Deployment: ", deployment_status)

        return EcsPanel(grid, title="Basic info")

    def tasks(self):
        if not self.data.fetcher.get("tasks"):
            return EcsPanel(NO_DATA_AVAILABLE, title="Tasks")

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
        content = (
            AsciiPlotIntegration(self.data.fetcher["cloudwatch_memory_data"])
            if self.data.fetcher.get("cloudwatch_memory_data")
            else NO_DATA_AVAILABLE
        )
        return EcsPanel(
            content,
            title="MemoryUtilization",
        )

    def cpu(self):
        content = (
            AsciiPlotIntegration(self.data.fetcher["cloudwatch_cpu_data"])
            if self.data.fetcher.get("cloudwatch_cpu_data")
            else NO_DATA_AVAILABLE
        )
        return EcsPanel(
            content,
            title="CPUUtilization",
        )

    def logs(self):
        if not self.data.fetcher.get("logs"):
            return EcsPanel(NO_DATA_AVAILABLE, title="Last logs")

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

        self.base_layout["main_left_basic_info"].update(self.basic_info())
        self.base_layout["main_left_tasks"].update(self.tasks())

        self.base_layout["main_right_top_memory"].update(self.memory())
        self.base_layout["main_right_top_cpu"].update(self.cpu())

        self.base_layout["main_right_bottom"].update(self.logs())

        return self.base_layout


class ListingLayout(BaseLayout):
    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_row(f"Clusters > {self.data.click_params['cluster']} > Services")

        return EcsPanel(grid)

    def main(self):
        table = Table()

        table.add_column("Service name")
        table.add_column("Task definition")
        table.add_column("Status")
        table.add_column("Tasks")
        table.add_column("Service type")
        table.add_column("Launch type")

        for service in self.data.fetcher:
            status = ServiceStatusEnum[service["status"]].value
            table.add_row(
                service["serviceName"],
                service["taskDefinition"].rsplit("task-definition/", 1)[-1],
                f"[{status.colour}]{status.icon}[/{status.colour}]  ({service['status'].lower()})",
                f"{service['runningCount']}/{service['desiredCount']} ({service['pendingCount']} pending)",
                service["schedulingStrategy"],
                service["launchType"],
            )

        return table

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())
        self.base_layout["main"].update(self.main())

        return self.base_layout
