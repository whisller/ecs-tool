from itertools import zip_longest


def _paginate(ecs_client, service, **kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    paginator = ecs_client.get_paginator(service)
    pagination_config = {"MaxItems": 100, "PageSize": 100}

    resp = paginator.paginate(**kwargs, PaginationConfig=pagination_config)
    yield resp

    while "NextToken" in resp:
        yield paginator.paginate(
            {
                **kwargs,
                **{"PaginationConfig": pagination_config},
                **{"StartingToken": resp["NextToken"]},
            }
        )


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    https://docs.python.org/3/library/itertools.html
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
