class EcsToolException(Exception):
    pass


class WaiterException(EcsToolException):
    """
    Exception used when we reached maximum number of attempts and task didn't reach STOPPED status.
    """


class TasksCannotBeRunException(EcsToolException):
    """
    Exception used when task cannot be run.
    """


class NoResultsException(EcsToolException):
    """
    Exception raised when no results found
    """
