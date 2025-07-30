'''Internal utilities for the workflows module.'''

import os
from typing import Any, Optional
from functools import cache
import jwt

# Memoized token_id to avoid repeated JWT parsing
_cached_token_id: Optional[str] = None


@cache
def get_token_id_from_env() -> Optional[str]:
    """Extract token_id from JWT token in TOKEN environment variable.
    Memoizes the result to avoid repeated parsing.

    Returns:
        Optional[str]: The token_id if found, None otherwise.
    """
    raw = os.getenv("TOKEN", "")
    if raw.startswith("Bearer "):
        token = raw[len("Bearer "):]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload.get("token_id")
        except jwt.PyJWTError:
            return None
    return None


def get_service_ref(service) -> str:
    '''get service_ref (name) if it's of proper shape (string, or
    callable with metadata), if not throw error

    Args:
        service (Union[Callable, str]): The service to validate.

    Raises:
        ValueError: If the service is neither a callable nor a string.

    Returns:
        str: The reference of the service to call.
    '''
    if callable(service):
        service_ref = service.__name__
    elif isinstance(service, str):
        service_ref = service
    else:
        raise ValueError(
            "Service to run must be either a callable or a string (service name)")
    return service_ref


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dictionaries with precedence, ignoring None values."""
    merged: dict[str, Any] = {}
    for config in configs:
        if config:
            for key, value in config.items():
                # Only update if the new value is not None
                if value is not None:
                    merged[key] = value
    return merged
