from new_ecs_tool.utils import _paginate


def fetch(ecs_client, click_params):
    services = ecs_client.describe_services(cluster=click_params["cluster"], services=[click_params["service"]])

    pagination = _paginate(
        ecs_client,
        "list_tasks",
        cluster=click_params["cluster"],
        desiredStatus="RUNNING",
        serviceName=click_params["service"],
    )

    arns = []
    for iterator in pagination:
        for task in iterator:
            arns += task["taskArns"]
    described_tasks = ecs_client.describe_tasks(cluster=click_params["cluster"], tasks=arns)

    return {
        "services": services,
        "tasks": described_tasks
    }
