def fetch(ecs_client, click_params):
    response = ecs_client.describe_services(cluster=click_params["cluster"], services=[click_params["service"]])
    return response
