#!/usr/bin/env python3
"""
ValiotRedisClient: unified sync/async Redis helper for ValiotWorkflows
- atomic large-object storage/retrieval (with chunking)
- default TTL (48h)
- per-workflow-run cleanup registry
- sync and async APIs
- returns full_key on store
- prefix syntax "wrid-<run_id>:" allows detection of already-prefixed keys
"""
from typing import Optional, Union
import re
import redis
import redis.asyncio as aioredis

from .redis_base import (
    store_large_atomic,
    retrieve_large,
    async_store_large_atomic,
    async_retrieve_large
)

DEFAULT_TTL = 48 * 3600  # 48 hours in seconds

# sentinel value for missing TTL (damn, javascript was right all this time)
_MISSING = object()


class ValiotRedisClient:
    """
    A Redis helper client that provides workflow-scoped storage with automatic key prefixing.

    This client provides both synchronous and asynchronous APIs for:
    - Large object storage with automatic chunking
    - Key prefixing with workflow run ID for isolation
    - TTL management with configurable expiration
    - Cleanup registry for workflow run cleanup
    - Atomic operations for data consistency

    Key features:
    - Automatic key prefixing with "wrid-<run_id>:" format
    - Large object chunking for objects > Redis value size limits
    - Cleanup tracking for automatic workflow run cleanup
    - Both sync and async method variants
    - Transparent handling of prefixed/non-prefixed keys

    Args:
        workflow_run_id: Unique identifier for the workflow run
        redis_client: Synchronous Redis client instance
        async_redis_client: Asynchronous Redis client instance
        default_ttl: Default time-to-live for stored objects (seconds)
    """

    def __init__(
        self,
        workflow_run_id: str,
        redis_client: redis.Redis,
        async_redis_client: aioredis.Redis,
        default_ttl: int = DEFAULT_TTL,
    ):
        """
        Initialize the ValiotRedisClient with workflow run context.

        Args:
            workflow_run_id: Unique identifier for the workflow run
            redis_client: Synchronous Redis client instance
            async_redis_client: Asynchronous Redis client instance
            default_ttl: Default TTL in seconds (default: 48 hours)
        """
        self.run_id = workflow_run_id
        self._r = redis_client
        self._ar = async_redis_client
        self.ttl = default_ttl
        self._cleanup_set = self._get_cleanup_set()
        self._prefix = f"wrid-{self.run_id}:"

    def _get_cleanup_set(self, wfr_id: str | None = None) -> str:
        """
        Get the cleanup set key for a workflow run ID.

        Args:
            wfr_id: Workflow run ID (uses current run if None)

        Returns:
            The cleanup set key in format "wrid-<run_id>:cleanup"
        """
        target_run_id = wfr_id if wfr_id is not None else self.run_id
        return f"wrid-{target_run_id}:cleanup"

    def _prefixed(self, key: str) -> str:
        """
        Add workflow run prefix to key if not already prefixed.

        Args:
            key: The base key name

        Returns:
            The prefixed key name in format "wrid-<run_id>:<key>"
        """
        # avoid double prefix - use regex to check for any wrid- prefix pattern
        return key if re.match(r"wrid-\d+:", key) else f"{self._prefix}{key}"

    # --- Sync large-object APIs ---
    def store_large(
        self,
        key: str,
        data: Union[bytes, str],
        chunk_size: int = 1 << 20,
        ttl: Optional[int] = _MISSING,  # type: ignore
    ) -> str:
        """
        Store large data atomically with chunking and return the full Redis key.

        Large objects are automatically chunked into smaller pieces to avoid Redis
        value size limitations. Metadata is stored separately to track chunks.

        Args:
            key: Base key name (will be prefixed with workflow run ID)
            data: Data to store (bytes or string)
            chunk_size: Size of each chunk in bytes (default: 1MB)
            ttl: Time-to-live in seconds (uses default_ttl if None)

        Returns:
            The full prefixed key used in Redis storage

        Raises:
            ValueError: If ttl is negative
        """
        if ttl is not None and ttl is not _MISSING and ttl < 0:
            raise ValueError("TTL cannot be negative")

        full_key = self._prefixed(key)

        # 2) Figure out what actual_ttl should be:
        actual_ttl = self.ttl if ttl is _MISSING else ttl

        store_large_atomic(
            self._r, full_key, data,
            chunk_size=chunk_size,
            ttl=actual_ttl
        )
        return full_key

    def retrieve_large(self, key: str) -> bytes | None:
        """
        Retrieve large data by reconstructing from chunks.

        Handles both base keys and full prefixed keys transparently.

        Args:
            key: Base key name or full prefixed key

        Returns:
            The reconstructed data as bytes

        Raises:
            KeyError: If the key doesn't exist
            redis.RedisError: If Redis operation fails
        """
        full_key = self._prefixed(key)
        return retrieve_large(self._r, full_key)

    def delete_large(self, key: str) -> None:
        """
        Atomically delete a large stored payload including all chunks and metadata.

        This operation removes all chunks, metadata, and the main key in a single
        atomic transaction to ensure consistency.

        Args:
            key: Base key name or full prefixed key to delete
        """
        full_key = self._prefixed(key)
        # collect keys to delete
        meta_key = f"{full_key}:meta"
        meta = self._r.hgetall(meta_key)
        to_delete = []
        if meta:
            n = int(meta[b"chunks"])
            to_delete = [f"{full_key}:{idx}" for idx in range(n)] + [meta_key]
        else:
            to_delete = [full_key]
        # atomic deletion
        pipe = self._r.pipeline(transaction=True)
        pipe.multi()
        for k in to_delete:
            pipe.delete(k)
        pipe.execute()

    def key_exists(self, key: str) -> bool:
        """
        Check if a key exists, handling both chunked and non-chunked storage.

        Args:
            key: Base key name or full prefixed key

        Returns:
            True if the key exists (either as chunked or simple storage)
        """
        full_key = self._prefixed(key)
        return bool(self._r.exists(f"{full_key}:meta") or self._r.exists(full_key))

    def mark_for_cleanup(self, key: str) -> None:
        """
        Mark a key for cleanup when the workflow run completes.

        Adds the key to the cleanup registry set with TTL. This allows
        automatic cleanup of all workflow-related data.

        Args:
            key: Base key name to mark for cleanup
        """
        full_key = self._prefixed(key)
        self._r.sadd(self._cleanup_set, full_key)
        self._r.expire(self._cleanup_set, self.ttl)

    def cleanup_run(self, wfr_id: str | None = None, clean_all: bool = False) -> None:
        """
        Clean up all data for this workflow run.

        Removes all keys that were marked for cleanup, including their chunks
        and metadata. This operation is atomic to ensure consistency.

        Args:
            wfr_id: Workflow run ID to clean up (uses current run if None)
            clean_all: If True, clean all keys for the run instead of just marked keys
        """
        # Determine which workflow run ID to use
        target_run_id = wfr_id if wfr_id is not None else self.run_id
        target_cleanup_set = self._get_cleanup_set(target_run_id)

        keys_to_clean = []

        if clean_all:
            # Get all large keys for this run
            keys_to_clean = self.list_large_keys_for_run(target_run_id)
        else:
            # Get keys from cleanup set
            members = self._r.smembers(target_cleanup_set)
            keys_to_clean = [member.decode() for member in members]

        # atomic cleanup
        pipe = self._r.pipeline(transaction=True)
        pipe.multi()

        for full_key in keys_to_clean:
            # delete each large payload
            meta_key = f"{full_key}:meta"
            meta = self._r.hgetall(meta_key)
            if meta:
                n = int(meta[b"chunks"])
                for idx in range(n):
                    pipe.delete(f"{full_key}:{idx}")
                pipe.delete(meta_key)
            else:
                pipe.delete(full_key)

        # Always delete the cleanup set for this run
        pipe.delete(target_cleanup_set)
        pipe.execute()

    # --- Utilities for listing and cleanup across workflow runs ---
    def list_active_run_ids(self) -> list[str]:
        """
        Scan Redis for all active workflow run IDs that have stored data.

        Identifies run IDs by scanning for metadata keys with the pattern
        "wrid-*:*:meta" across all workflow runs.

        Returns:
            List of active workflow run IDs found in Redis
        """
        run_ids: set[str] = set()
        cursor = 0
        pattern = "wrid-*:*:meta"
        while True:
            cursor, keys = self._r.scan(
                cursor=cursor, match=pattern, count=1000)
            for key in keys:
                k = key.decode() if isinstance(key, bytes) else key
                # k looks like "wrid-<runid>:<base>:meta"
                prefix_part = k.split(":", 1)[0]  # "wrid-<runid>"
                if prefix_part.startswith("wrid-"):
                    rid = prefix_part[len("wrid-"):]
                    run_ids.add(rid)
            if cursor == 0:
                break
        return list(run_ids)

    def list_large_keys_for_run(self, run_id: Optional[str] = None) -> list[str]:
        """
        Return all stored large-object keys for a specific workflow run.

        Args:
            run_id: Workflow run ID to list keys for (uses current run if None)

        Returns:
            List of full key names for all large objects stored for the run
        """
        rid = run_id if run_id is not None else self.run_id
        prefix = f"wrid-{rid}:"
        pattern = prefix + "*:meta"
        full_keys: list[str] = []
        cursor = 0
        while True:
            cursor, keys = self._r.scan(
                cursor=cursor, match=pattern, count=1000)
            for key in keys:
                k = key.decode() if isinstance(key, bytes) else key
                full = k[: -len(":meta")]
                full_keys.append(full)
            if cursor == 0:
                break
        return full_keys

    def cleanup_runs(self, run_ids: list[str]) -> None:
        """
        Perform cleanup for multiple workflow run IDs in batch.

        Creates temporary ValiotRedisClient instances for each run ID
        and performs cleanup for all specified runs.

        Args:
            run_ids: List of workflow run IDs to clean up
        """
        for rid in run_ids:
            client = ValiotRedisClient(rid, self._r, self._ar, self.ttl)
            client.cleanup_run()

# --- Async listing and cleanup across workflow runs ---
    async def async_list_active_run_ids(self) -> list[str]:
        """
        Asynchronously scan Redis for all active workflow run IDs.

        Async version of list_active_run_ids() that identifies run IDs
        by scanning for metadata keys across all workflow runs.

        Returns:
            List of active workflow run IDs found in Redis
        """
        run_ids: set[str] = set()
        cursor = 0
        pattern = "wrid-*:*:meta"
        while True:
            cursor, keys = await self._ar.scan(cursor=cursor, match=pattern, count=1000)
            for key in keys:
                k = key.decode() if isinstance(key, bytes) else key
                prefix_part = k.split(":", 1)[0]
                if prefix_part.startswith("wrid-"):
                    rid = prefix_part[len("wrid-"):]
                    run_ids.add(rid)
            if cursor == 0:
                break
        return list(run_ids)

    async def async_list_large_keys_for_run(self, run_id: Optional[str] = None) -> list[str]:
        """
        Asynchronously return all stored large-object keys for a workflow run.

        Args:
            run_id: Workflow run ID to list keys for (uses current run if None)

        Returns:
            List of full key names for all large objects stored for the run
        """
        rid = run_id if run_id is not None else self.run_id
        prefix = f"wrid-{rid}:"
        pattern = prefix + "*:meta"
        full_keys: list[str] = []
        cursor = 0
        while True:
            cursor, keys = await self._ar.scan(cursor=cursor, match=pattern, count=1000)
            for key in keys:
                k = key.decode() if isinstance(key, bytes) else key
                full = k[: -len(":meta")]
                full_keys.append(full)
            if cursor == 0:
                break
        return full_keys

    async def async_cleanup_runs(self, run_ids: list[str]) -> None:
        """
        Asynchronously perform cleanup for multiple workflow run IDs.

        Creates temporary ValiotRedisClient instances for each run ID
        and performs async cleanup for all specified runs.

        Args:
            run_ids: List of workflow run IDs to clean up
        """
        for rid in run_ids:
            client = ValiotRedisClient(rid, self._r, self._ar, self.ttl)
            await client.async_cleanup_run()

# --- Async large-object APIs (prefix "async_") ---
    async def async_store_large(
        self,
        key: str,
        data: Union[bytes, str],
        chunk_size: int = 1 << 20,
        ttl: Optional[int] = _MISSING,  # type: ignore
    ) -> str:
        """
        Asynchronously store large data with chunking and return the full Redis key.

        Async version of store_large() that handles large objects by chunking
        them into smaller pieces with atomic storage.

        Args:
            key: Base key name (will be prefixed with workflow run ID)
            data: Data to store (bytes or string)
            chunk_size: Size of each chunk in bytes (default: 1MB)
            ttl: Time-to-live in seconds (uses default_ttl if None)

        Returns:
            The full prefixed key used in Redis storage

        Raises:
            ValueError: If ttl is negative
        """
        if ttl is not None and ttl is not _MISSING and ttl < 0:
            raise ValueError("TTL cannot be negative")

        # 2) Figure out what actual_ttl should be:
        actual_ttl = self.ttl if ttl is _MISSING else ttl

        full_key = self._prefixed(key)
        await async_store_large_atomic(
            self._ar, full_key, data,
            chunk_size=chunk_size,
            ttl=actual_ttl
        )
        return full_key

    async def async_retrieve_large(self, key: str) -> bytes | None:
        """
        Asynchronously retrieve large data by reconstructing from chunks.

        Async version of retrieve_large() that handles both base keys
        and full prefixed keys transparently.

        Args:
            key: Base key name or full prefixed key

        Returns:
            The reconstructed data as bytes

        Raises:
            KeyError: If the key doesn't exist
            redis.RedisError: If Redis operation fails
        """
        full_key = self._prefixed(key)
        return await async_retrieve_large(self._ar, full_key)

    async def async_delete_large(self, key: str) -> None:
        """
        Asynchronously delete a large stored payload including chunks and metadata.

        Async version of delete_large() that removes all chunks, metadata,
        and the main key in a single atomic transaction.

        Args:
            key: Base key name or full prefixed key to delete
        """
        full_key = self._prefixed(key)
        meta_key = f"{full_key}:meta"
        meta = await self._ar.hgetall(meta_key)
        to_delete: List[str] = []
        if meta:
            n = int(meta[b"chunks"])
            to_delete = [f"{full_key}:{idx}" for idx in range(n)] + [meta_key]
        else:
            to_delete = [full_key]
        pipe = self._ar.pipeline(transaction=True)
        pipe.multi()
        for k in to_delete:
            pipe.delete(k)
        await pipe.execute()

    async def async_key_exists(self, key: str) -> bool:
        """
        Asynchronously check if a key exists in Redis.

        Async version of key_exists() that handles both chunked
        and non-chunked storage formats.

        Args:
            key: Base key name or full prefixed key

        Returns:
            True if the key exists (either as chunked or simple storage)
        """
        full_key = self._prefixed(key)
        meta_exists = await self._ar.exists(f"{full_key}:meta")
        plain_exists = await self._ar.exists(full_key)
        return bool(meta_exists or plain_exists)

    async def async_mark_for_cleanup(self, key: str) -> None:
        """
        Asynchronously mark a key for cleanup when the workflow run completes.

        Async version of mark_for_cleanup() that adds the key to the cleanup
        registry set with TTL for automatic cleanup.

        Args:
            key: Base key name to mark for cleanup
        """
        full_key = self._prefixed(key)
        await self._ar.sadd(self._cleanup_set, full_key)
        await self._ar.expire(self._cleanup_set, self.ttl)

    async def async_cleanup_run(self, wfr_id: str | None = None, clean_all: bool = False) -> None:
        """
        Asynchronously clean up all data for this workflow run.

        Async version of cleanup_run() that removes all keys marked for cleanup,
        including their chunks and metadata in an atomic operation.

        Args:
            wfr_id: Workflow run ID to clean up (uses current run if None)
            clean_all: If True, clean all keys for the run instead of just marked keys
        """
        # Determine which workflow run ID to use
        target_run_id = wfr_id if wfr_id is not None else self.run_id
        target_cleanup_set = self._get_cleanup_set(target_run_id)

        keys_to_clean = []

        if clean_all:
            # Get all large keys for this run
            keys_to_clean = await self.async_list_large_keys_for_run(target_run_id)
        else:
            # Get keys from cleanup set
            members = await self._ar.smembers(target_cleanup_set)
            keys_to_clean = [member.decode() for member in members]

        pipe = self._ar.pipeline(transaction=True)
        pipe.multi()

        for full_key in keys_to_clean:
            meta_key = f"{full_key}:meta"
            meta = await self._ar.hgetall(meta_key)
            if meta:
                n = int(meta[b"chunks"])
                for idx in range(n):
                    pipe.delete(f"{full_key}:{idx}")
                pipe.delete(meta_key)
            else:
                pipe.delete(full_key)

        # Always delete the cleanup set for this run
        pipe.delete(target_cleanup_set)
        await pipe.execute()
