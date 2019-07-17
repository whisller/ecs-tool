from textwrap import wrap

from colorclass import Color
from terminaltables import SingleTable

SERVICE_STATUS_COLOUR = {
    "ACTIVE": "autogreen",
    "DRAINING": "autoyellow",
    "INACTIVE": "autored",
}

TASK_STATUS_COLOUR = {
    "PROVISIONING": "autoblue",
    "PENDING": "automagenta",
    "ACTIVATING": "autoyellow",
    "RUNNING": "autogreen",
    "DEACTIVATING": "autoyellow",
    "STOPPING": "automagenta",
    "DEPROVISIONING": "autoblue",
    "STOPPED": "autored",
}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class EcsTable(SingleTable):
    def __init__(self, data):
        super().__init__(data)

        self.inner_row_border = False
        self.inner_column_border = False
        self.outer_border = False
        self.inner_heading_row_border = True


class ServicesTable(EcsTable):
    HEADER = (
        "Service name",
        "Task definition",
        "Status",
        "D",
        "P",
        "R",
        "Service type",
        "Launch type",
    )

    @classmethod
    def build(cls, services):
        data = [ServicesTable.HEADER]

        for service in services:
            status_colour = SERVICE_STATUS_COLOUR.get(service["status"])

            data.append(
                [
                    service["serviceName"],
                    service["taskDefinition"].rsplit("task-definition/", 1)[-1],
                    Color(
                        f"{{{status_colour}}}{service['status']}{{/{status_colour}}}"
                    ),
                    service["desiredCount"],
                    service["pendingCount"],
                    service["runningCount"],
                    service["schedulingStrategy"],
                    service["launchType"],
                ]
            )

        return cls(data)


class TasksTable(EcsTable):
    HEADER = (
        "Task",
        "Task definition",
        "Status",
        "Command",
        "Started at",
        "Stopped at",
        "Execution time",
        "Termination reason",
    )

    @classmethod
    def build(cls, tasks):
        data = [TasksTable.HEADER]

        for task in tasks:
            status_colour = TASK_STATUS_COLOUR.get(task["lastStatus"])
            termination_code = (
                "(" + str(task.get("containers")[0].get("exitCode")) + ")"
                if "exitCode" in task.get("containers")[0]
                else ""
            )

            termination_reason = (
                _wrap(task.get("stoppedReason"), 10)
                + " "
                + _wrap(task.get("containers")[0].get("reason"), 10)
                + termination_code
            )

            data.append(
                [
                    task["taskArn"].rsplit("task/", 1)[-1],
                    task["taskDefinitionArn"].rsplit("task-definition/", 1)[-1],
                    Color(
                        f"{{{status_colour}}}{task['lastStatus']}{{/{status_colour}}}"
                    ),
                    " ".join(
                        task["overrides"]["containerOverrides"][0].get("command", "")
                    ),
                    task.get("startedAt").strftime(DATE_FORMAT)
                    if task.get("startedAt")
                    else "",
                    task.get("stoppedAt").strftime(DATE_FORMAT)
                    if task.get("stoppedAt")
                    else "",
                    task.get("stoppedAt") - task.get("startedAt")
                    if all((task.get("startedAt"), task.get("stoppedAt")))
                    else "",
                    termination_reason,
                ]
            )

        return cls(data)


class TaskDefinitionsTable(EcsTable):
    HEADER = ("Task definition",)

    @classmethod
    def build(cls, task_definitions):
        data = [TaskDefinitionsTable.HEADER]

        for definition in task_definitions:
            data.append([definition.rsplit("task-definition/", 1)[-1]])

        return cls(data)


def _wrap(text, size):
    if not text:
        return ""

    return "\n".join(wrap(text, size))
