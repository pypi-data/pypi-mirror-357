#!/usr/bin/env python3
"""
Utilities to atomically store and retrieve arbitrarily large byte payloads in Redis
with chunking, cleanup, TTL support, and integrity checks.
Provides both synchronous and asynchronous APIs.
"""
import math
from typing import Optional, Union

import redis
import redis.asyncio as aioredis


class RedisLargeObjectError(Exception):
    """Custom exception for large object storage/retrieval issues."""
    pass


def _validate_args(
    base_key: str,
    data: Union[bytes, str],
    chunk_size: int,
    max_chunks: int,
) -> bytes:
    """
    Validate common arguments and return data as bytes.
    Raises RedisLargeObjectError on invalid input.
    """
    if not isinstance(base_key, str) or not base_key:
        raise RedisLargeObjectError("base_key must be a non-empty string")
    if isinstance(data, str):
        data = data.encode('utf-8')
    if not isinstance(data, (bytes, bytearray)):
        raise RedisLargeObjectError("data must be bytes or str")
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise RedisLargeObjectError("chunk_size must be a positive integer")
    total = len(data)
    n_chunks = math.ceil(total / chunk_size)
    if n_chunks > max_chunks:
        raise RedisLargeObjectError(
            f"Too many chunks ({n_chunks}) exceeds max_chunks={max_chunks}"
        )
    return data


def store_large_atomic(
    r: redis.Redis,
    base_key: str,
    data: Union[bytes, str],
    chunk_size: int = 1 << 20,
    ttl: Optional[int] = None,
    max_chunks: int = 10000,
) -> None:
    """
    Synchronous: atomically store a large payload by chunking it.
    """
    data = _validate_args(base_key, data, chunk_size, max_chunks)
    total = len(data)
    n_chunks = math.ceil(total / chunk_size)
    meta_key = f"{base_key}:meta"
    old_meta = r.hgetall(meta_key)
    old_n = int(old_meta.get(b"chunks", 0)) if old_meta else 0

    pipe = r.pipeline(transaction=True)
    pipe.multi()
    for idx in range(old_n):
        if idx >= n_chunks:
            pipe.delete(f"{base_key}:{idx}")
    for idx in range(n_chunks):
        start = idx * chunk_size
        pipe.set(f"{base_key}:{idx}", data[start:start+chunk_size])
    pipe.hset(meta_key, mapping={"chunks": n_chunks, "size": total})
    if ttl is not None:
        pipe.expire(meta_key, ttl)
        for idx in range(n_chunks):
            pipe.expire(f"{base_key}:{idx}", ttl)
    else:
        # If we want "no expiration", explicitly PERSIST the meta key
        # (chunk keys were just SET, so their old TTL is already cleared)
        pipe.persist(meta_key)
    try:
        pipe.execute()
    except Exception as e:
        raise RedisLargeObjectError(f"Redis transaction failed: {e}") from e


def retrieve_large(
    r: redis.Redis,
    base_key: str,
) -> bytes | None:
    """
    Synchronous: retrieve a payload stored via store_large_atomic.
    """
    if not isinstance(base_key, str) or not base_key:
        raise RedisLargeObjectError("base_key must be a non-empty string")
    meta_key = f"{base_key}:meta"
    meta = r.hgetall(meta_key)
    if not meta:
        single = r.get(base_key)
        return single or None
    try:
        n_chunks = int(meta[b"chunks"])
    except Exception as e:
        raise RedisLargeObjectError(
            "Invalid meta record: missing 'chunks'") from e
    pipe = r.pipeline()
    for idx in range(n_chunks):
        pipe.get(f"{base_key}:{idx}")
    try:
        parts = pipe.execute()
    except Exception as e:
        raise RedisLargeObjectError(f"Redis retrieval failed: {e}") from e
    for idx, part in enumerate(parts):
        if part is None:
            raise RedisLargeObjectError(
                f"Missing chunk {idx} for base_key={base_key}")
    return b"".join(parts) or None


async def async_store_large_atomic(
    r: aioredis.Redis,
    base_key: str,
    data: Union[bytes, str],
    chunk_size: int = 1 << 20,
    ttl: Optional[int] = None,
    max_chunks: int = 10000,
) -> None:
    """
    Asynchronous: atomically store a large payload by chunking it.
    """
    data = _validate_args(base_key, data, chunk_size, max_chunks)
    total = len(data)
    n_chunks = math.ceil(total / chunk_size)
    meta_key = f"{base_key}:meta"
    old_meta = await r.hgetall(meta_key)
    old_n = int(old_meta.get(b"chunks", 0)) if old_meta else 0

    pipe = r.pipeline(transaction=True)
    pipe.multi()
    for idx in range(old_n):
        if idx >= n_chunks:
            pipe.delete(f"{base_key}:{idx}")
    for idx in range(n_chunks):
        start = idx * chunk_size
        pipe.set(f"{base_key}:{idx}", data[start:start+chunk_size])
    pipe.hset(meta_key, mapping={"chunks": n_chunks, "size": total})
    if ttl is not None:
        pipe.expire(meta_key, ttl)
        for idx in range(n_chunks):
            pipe.expire(f"{base_key}:{idx}", ttl)
    else:
        # If we want "no expiration", explicitly PERSIST the meta key
        # (chunk keys were just SET, so their old TTL is already cleared)
        pipe.persist(meta_key)
    try:
        await pipe.execute()
    except Exception as e:
        raise RedisLargeObjectError(f"Redis transaction failed: {e}") from e


async def async_retrieve_large(
    r: aioredis.Redis,
    base_key: str,
) -> bytes | None:
    """
    Asynchronous: retrieve a payload stored via async_store_large_atomic.
    """
    if not isinstance(base_key, str) or not base_key:
        raise RedisLargeObjectError("base_key must be a non-empty string")
    meta_key = f"{base_key}:meta"
    meta = await r.hgetall(meta_key)
    if not meta:
        single = await r.get(base_key)
        return single or None
    try:
        n_chunks = int(meta[b"chunks"])
    except Exception as e:
        raise RedisLargeObjectError(
            "Invalid meta record: missing 'chunks'") from e
    pipe = r.pipeline()
    for idx in range(n_chunks):
        pipe.get(f"{base_key}:{idx}")
    try:
        parts = await pipe.execute()
    except Exception as e:
        raise RedisLargeObjectError(f"Redis retrieval failed: {e}") from e
    for idx, part in enumerate(parts):
        if part is None:
            raise RedisLargeObjectError(
                f"Missing chunk {idx} for base_key={base_key}")
    return b"".join(parts) or None
