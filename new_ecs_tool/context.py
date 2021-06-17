import boto3


class ContextObject:
    def __init__(self):
        self._ecs = boto3.client("ecs")

    @property
    def ecs(self):
        return self._ecs
