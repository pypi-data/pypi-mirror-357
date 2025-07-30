"""
Function utility shenanigans, for the services implementation.

This module provides utilities for creating exact copies of functions,
ensuring they are pickleable.
"""
import sys
from dataclasses import replace
from types import FunctionType
from typing import Callable


def create_copy_func(func: Callable, new_name: str | None = None) -> Callable:
    """Create an exact and clean copy of a function, ensuring it's pickleable."""
    module = sys.modules[func.__module__]
    new_func = FunctionType(
        func.__code__,
        func.__globals__,
        new_name.replace('.', '_') if new_name else func.__name__,
        func.__defaults__,
        func.__closure__,
    )
    new_func.__dict__.update(func.__dict__)

    if hasattr(func, '__temporal_activity_definition'):
        activity_defn = func.__temporal_activity_definition  # pylint: disable=W0212
        activity_defn_copy = replace(activity_defn)
        # pylint: disable=W0212
        new_func.__temporal_activity_definition = activity_defn_copy  # type: ignore

    # Register in globals so pickle can find it
    safe_name = new_name.replace('.', '_') if new_name else func.__name__
    new_func.__name__ = safe_name
    new_func.__qualname__ = safe_name
    # Monkey-patch the real module
    setattr(module, safe_name, new_func)

    return new_func
