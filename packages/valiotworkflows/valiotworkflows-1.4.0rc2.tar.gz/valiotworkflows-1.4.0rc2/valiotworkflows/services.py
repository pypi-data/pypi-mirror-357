"""
Service utilities for ValiotWorkflows.

This module provides service-related utilities and functions for ValiotWorkflows.
It centralizes imports to allow for easier usage patterns and future-proofing.
"""
from typing import Any

# Re-export from temporalio
from temporalio import activity as temporalio_activity

# Re-export from valiotworkflows
from .service_decorator import (
    service,
    static_workflow_service,
    workflows_studio_service,
    custom_service,
    ServiceCallable,
)
from .execution_mode import ServiceExecutionMode
from .service_handler import ServiceHandler
from .base_service_plugin_mixin import BaseServicePluginMixin


def heartbeat(*args: Any) -> None:
    """
    Record a heartbeat for the current activity.

    This is a wrapper around temporalio's heartbeat function to allow for future-proofing.

    Args:
        *args: Details to include with the heartbeat.

    Raises:
        RuntimeError: If not called from within an activity.
    """
    # Simply delegate to temporalio's heartbeat implementation
    temporalio_activity.heartbeat(*args)


# More convenience functions can be added here as needed

__all__ = [
    # Core service components
    "ServiceHandler",
    "ServiceExecutionMode",
    "BaseServicePluginMixin",

    # Service decorators
    "service",
    "static_workflow_service",
    "workflows_studio_service",
    "custom_service",
    "ServiceCallable",

    # Activity utilities
    "heartbeat",
]
