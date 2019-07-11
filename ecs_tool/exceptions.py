class EcsToolException(Exception):
    pass


class WaiterException(EcsToolException):
    """
    Exception used when we reached maximum number of attempts and task didn't reach STOPPED status.
    """


class TaskDefinitionInactiveException(EcsToolException):
    """
    Task definition is inactive, we can't run task.
    """


class NoTaskDefinitionFoundException(EcsToolException):
    """
    No task definition found.
    """


class NoResultsException(EcsToolException):
    """
    Exception raised when no results found
    """
