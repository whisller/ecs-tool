import os

import boto3


class ContextObject:
    def __init__(self):
        self._ecs = boto3.client("ecs")
        self._cloudwatch = boto3.client("cloudwatch")
        self._logs = boto3.client("logs")

    @property
    def ecs(self):
        return self._ecs

    @property
    def cloudwatch(self):
        return self._cloudwatch

    @property
    def logs(self):
        return self._logs

    @property
    def aws_region(self):
        return os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))

    @property
    def aws_account_id(self):
        return boto3.client("sts").get_caller_identity().get("Account")
