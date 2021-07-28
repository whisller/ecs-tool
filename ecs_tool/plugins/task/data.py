from ...context import ContextObject
from ...exception import EcsToolException


def _fetch_latest_active_task_definition(ecs_client, name):
    response = ecs_client.list_task_definitions(familyPrefix=name, status="ACTIVE", sort="DESC", maxResults=1)

    if not response["taskDefinitionArns"]:
        raise EcsToolException(f'Unable to find active task definition with name "{name}".')

    return response["taskDefinitionArns"][0].rsplit(":", 1)[0]


def fetch_run_task(context: ContextObject, click_params):
    if not getattr(fetch_run_task, "task_ran", False):
        args = {"cluster": click_params["cluster"]}

        try:
            _, _ = click_params["task_definition"].split(":")
            args["taskDefinition"] = click_params["task_definition"]
        except ValueError:
            args["taskDefinition"] = _fetch_latest_active_task_definition(context.ecs, click_params["task_definition"])

        if click_params["command"]:
            args["overrides"] = {
                "containerOverrides": [
                    {"name": args["taskDefinition"].rsplit(":", 1)[0], "command": click_params["command"]}
                ]
            }

        result = context.ecs.run_task(**args)

        fetch_run_task.task_ran = True
        fetch_run_task.task_arn = result["tasks"][0]["taskArn"]

    task = context.ecs.describe_tasks(cluster=click_params["cluster"], tasks=[fetch_run_task.task_arn])["tasks"][0]

    return {"task": task}
