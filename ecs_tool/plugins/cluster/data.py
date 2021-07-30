from ...context import ContextObject
from ...data_loader import fetch_listing as base_fetch_listing


def fetch_listing(context: ContextObject, click_params):
    return base_fetch_listing(
        context.ecs,
        paginator_type="list_clusters",
        arn_index="clusterArns",
        describe_function=context.ecs.describe_clusters,
        describe_filter="clusters",
        result_key="clusters",
    )
