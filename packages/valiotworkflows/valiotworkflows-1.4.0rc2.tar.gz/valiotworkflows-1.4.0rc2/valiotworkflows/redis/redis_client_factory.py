"""
redis_client_factory.py

Provides singleton-like accessors for Redis clients (sync and async)
and for ValiotRedisClient instances per workflow_run_id.
If Redis is unavailable, returns None to avoid breaking execution.
"""
import os
import threading
from typing import Optional
import redis
import redis.asyncio as aioredis
from .valiot_redis_client import ValiotRedisClient

# Module-level singletons and lock for thread safety
_sync_client: Optional[redis.Redis] = None
_async_client: Optional[aioredis.Redis] = None
_clients_lock = threading.Lock()
_valiot_clients: dict[str, ValiotRedisClient] = {}

os_env_redis_host = os.getenv("REDIS_HOST", "localhost")
os_env_redis_port = int(os.getenv("REDIS_PORT", '6379'))


def has_sync_client_instance() -> bool:
    """Returns True if we've already created the sync Redis client."""
    return _sync_client is not None


def has_async_client_instance() -> bool:
    """Returns True if we've already created the async Redis client."""
    return _async_client is not None


def get_sync_client_instance() -> Optional[redis.Redis]:
    """
    Returns a singleton synchronous Redis client, or None if instantiation fails.
    """
    global _sync_client  # pylint: disable=global-statement
    if _sync_client is None:
        with _clients_lock:
            if _sync_client is None:
                try:
                    _sync_client = redis.Redis(
                        host=os_env_redis_host, port=os_env_redis_port, decode_responses=False)
                    # Optionally test connection
                    _sync_client.ping()
                except Exception:
                    _sync_client = None
    return _sync_client


def get_async_client_instance() -> Optional[aioredis.Redis]:
    """
    Returns a singleton asynchronous Redis client, or None if instantiation fails.
    """
    global _async_client  # pylint: disable=global-statement
    if _async_client is None:
        with _clients_lock:
            if _async_client is None:
                try:
                    _async_client = aioredis.Redis(
                        host=os_env_redis_host, port=os_env_redis_port, decode_responses=False)
                    # Optionally test connection
                    # await _async_client.ping()  # can't await here
                except Exception:
                    _async_client = None
    return _async_client


def get_valiot_redis_client_for(run_id: str) -> ValiotRedisClient:
    """
    Returns a singleton ValiotRedisClient for a given workflow_run_id.
    Raises RuntimeError if Redis clients are unavailable.
    """
    sync_r = get_sync_client_instance()
    async_r = get_async_client_instance()
    if sync_r is None or async_r is None:
        raise RuntimeError("Redis clients are unavailable")
    # Use lock to protect creation
    with _clients_lock:
        if run_id not in _valiot_clients:
            _valiot_clients[run_id] = ValiotRedisClient(
                workflow_run_id=run_id,
                redis_client=sync_r,
                async_redis_client=async_r
            )
        return _valiot_clients[run_id]
