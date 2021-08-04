from enum import Enum

from rich.table import Table

from ...ui import BaseLayout, EcsPanel, StatusEnum


class ClusterStatusEnum(Enum):
    ACTIVE = StatusEnum.ACTIVE.value
    PROVISIONING = StatusEnum.IN_PROGRESS.value
    DEPROVISIONING = StatusEnum.IN_PROGRESS.value
    FAILED = StatusEnum.STOPPED.value
    INACTIVE = StatusEnum.STOPPED.value


class ListingLayout(BaseLayout):
    def header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_row(f"Clusters")

        return EcsPanel(grid)

    def main(self):
        table = Table()

        table.add_column("Cluster name")
        table.add_column("Status")
        table.add_column("Running tasks")
        table.add_column("Pending tasks")
        table.add_column("Active services")

        for cluster in self.data.fetcher:
            status = ClusterStatusEnum[cluster["status"]].value

            table.add_row(
                cluster["clusterName"],
                f"[{status.colour}]{status.icon}[/{status.colour}]  ({cluster['status'].lower()})",
                str(cluster["runningTasksCount"]),
                str(cluster["pendingTasksCount"]),
                str(cluster["activeServicesCount"]),
            )

        return table

    def load(self, data):
        self.data = data
        self.base_layout["header"].update(self.header())
        self.base_layout["main"].update(self.main())

        return self.base_layout
