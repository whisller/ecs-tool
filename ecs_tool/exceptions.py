class EcsToolException:
    pass


class WaitParameterException(EcsToolException):
    """
    Exception used when "describe_tasks" returns more than one task.
    """


class NoResultsException(EcsToolException):
    """
    Exception raised when no results found
    """
