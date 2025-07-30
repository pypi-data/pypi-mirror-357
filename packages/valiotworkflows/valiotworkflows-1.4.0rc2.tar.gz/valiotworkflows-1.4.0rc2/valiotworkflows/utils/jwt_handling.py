"""
JWT handling utilities for ValiotWorkflows.

This module provides utilities for handling JWT tokens,
including getting the token id of the active auth token.
"""
import os
import jwt


def get_own_token_id() -> str | None:
    """Get the token id of the current worker.

    Returns:
        str: The token id of the current worker.
    """
    token = os.environ.get("TOKEN", "").split("Bearer ")[1]
    if not token:
        return None
    decoded = jwt.decode(jwt=token, algorithms=["HS512"], options={
                         "verify_signature": False})
    return decoded.get("token_id", None)
