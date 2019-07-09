def _paginate(ecs_client, service, **kwargs):
    paginator = ecs_client.get_paginator(service)
    pagination_config = {"MaxItems": 100, "PageSize": 100}

    resp = paginator.paginate(**kwargs, PaginationConfig=pagination_config)
    yield resp

    while "NextToken" in resp:
        yield paginator.paginate(
            {**kwargs, **{"PaginationConfig": pagination_config}, **{"StartingToken": resp["NextToken"]}}
        )


def fetch_services(ecs_client, cluster, launch_type=None, scheduling_strategy=None):
    paginator = ecs_client.get_paginator("list_services")

    args = {"cluster": cluster}

    if launch_type:
        args["launchType"] = launch_type

    if scheduling_strategy:
        args["schedulingStrategy"] = scheduling_strategy

    pagination_config = {"MaxItems": 100, "PageSize": 100}



    resp = paginator.paginate(**args, PaginationConfig=pagination_config)

    while "NextToken" in resp:
        resp = paginator.paginate(
            {**args, **{"PaginationConfig": pagination_config}, **{"StartingToken": resp["NextToken"]}}
        )

