class EcsToolException:
    pass


class WaitParameterException(EcsToolException):
    """
    Exception used when "describe_tasks" returns more than one task.
    """
