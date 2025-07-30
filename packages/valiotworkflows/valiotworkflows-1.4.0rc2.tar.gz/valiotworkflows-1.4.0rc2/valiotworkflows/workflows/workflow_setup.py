from enum import Enum


class SetupResult(str, Enum):
    '''Enum to define the possible results of the setup function of a workflow.'''
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"  # Log a warning but allow the worker to proceed
    ERROR = "ERROR"      # Raise an exception and stop the worker
