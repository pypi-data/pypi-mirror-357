"""
Defines the execution mode for services/activities.
"""
from enum import Enum


class ServiceExecutionMode(str, Enum):
    """Execution mode for services/activities."""
    IO_BOUND = "IO_BOUND"  # Default: thread-based execution
    CPU_BOUND = "CPU_BOUND"  # Runs in separate process
    # Runs inline within workflow process (NOT IMPLEMENTED YET)
    LOCAL = "LOCAL"
