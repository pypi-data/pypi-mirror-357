"""
Date handling utilities for ValiotWorkflows.

This module provides utilities for handling dates and times,
including getting the current UTC date in string format.
"""
from datetime import datetime
import pytz


def get_current_utc_date() -> str:
    """Get the current UTC date in string format."""
    current_utc_datetime = datetime.now(pytz.utc)
    formatted_datetime = current_utc_datetime.isoformat(
        timespec='seconds').replace("+00:00", "Z")
    return formatted_datetime
