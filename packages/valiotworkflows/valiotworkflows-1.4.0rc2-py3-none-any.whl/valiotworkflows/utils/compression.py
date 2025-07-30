"""Compression utilities for ValiotWorkflows.

This module provides utilities for compressing and decompressing objects
using zlib compression and base64 encoding. It uses orjson for fast JSON
serialization/deserialization.
"""
import base64
import zlib
import asyncio
from typing import Any, Callable, Optional, TypeVar, Union
import orjson

T = TypeVar('T')


def compress(
    obj: Any,
    serializer: Optional[Callable[[Any], Union[str, bytes]]] = None
) -> bytes:
    """Compress the given object into a compressed bytes object.
    The compression is done using zlib.

    Args:
        obj (Any): The object to compress and encode.
        serializer (Optional[Callable[[Any], Union[str, bytes]]]): Custom serializer function.
            Can return either str or bytes. If None, uses orjson.dumps. Defaults to None.

    Returns:
        str: The compressed and base64-encoded string.

    Examples:
        >>> compress({"foo": "bar"}) # Returns base64 string
        >>> compress(user, custom_user_serializer) # Custom serializer
    """
    # Use provided serializer or default to orjson.dumps
    if serializer:
        serialized = serializer(obj)
    else:
        # If obj is bytes, decode to string first to avoid serialization issues
        if isinstance(obj, bytes):
            obj = obj.decode('utf-8')
        # orjson.dumps returns bytes directly
        serialized = orjson.dumps(obj)

    # Handle both str and bytes from serializer
    if isinstance(serialized, str):
        serialized_bytes = serialized.encode("utf-8")
    else:
        serialized_bytes = serialized

    compressed = zlib.compress(serialized_bytes)

    return base64.b64encode(compressed)


def decompress(
    compressed_data: Union[str, bytes, list[int], None],
    deserializer: Optional[Callable[[Union[str, bytes]], Any]] = None
) -> Any:
    """Decompress the given compressed data into the original object.
    The decompression is done using zlib.

    Args:
        compressed_data (Union[str, bytes, list[int]]): The base64-encoded compressed data.
            Can be a string, bytes, or list of integers (as received from temporalio).
        deserializer (Optional[Callable[[Union[str, bytes]], Any]]): Custom deserializer function.
            Can accept either str or bytes. If None, uses orjson.loads. Defaults to None.

    Returns:
        Any: The original object.

    Examples:
        >>> decompress(compressed_str) # Base64 string or bytes input
        >>> decompress(compressed_data, custom_user_deserializer) # Custom deserializer
        >>> decompress([1, 2, 3]) # List of integers from temporalio
    """
    if compressed_data is None:
        return None

    # Handle list of integers (from temporalio)
    if isinstance(compressed_data, list):
        compressed_data = bytes(compressed_data)

    # Handle both str (base64) and bytes input
    if isinstance(compressed_data, str):
        # String input - decode as base64
        compressed_bytes = base64.b64decode(compressed_data)
    else:
        # Bytes input - assume it's already compressed bytes or try to decode as base64 string
        try:
            compressed_bytes = base64.b64decode(compressed_data)
        except Exception:
            # If it fails, assume it's already compressed bytes
            compressed_bytes = compressed_data

    decompressed_bytes = zlib.decompress(compressed_bytes)

    # Use provided deserializer or default to orjson.loads
    if deserializer:
        # Try to pass bytes first, fallback to str if needed
        try:
            return deserializer(decompressed_bytes)
        except (TypeError, ValueError):
            # If deserializer can't handle bytes, try str
            return deserializer(decompressed_bytes.decode("utf-8"))
    else:
        # orjson.loads can handle bytes directly
        return orjson.loads(decompressed_bytes)

# async version of the utilities:


async def async_compress(
    obj: Any,
    serializer: Optional[Callable[[Any], Union[str, bytes]]] = None
) -> bytes:
    """
    Async wrapper around `compress()`. Offloads to a thread to avoid blocking the event loop.
    """
    return await asyncio.to_thread(compress, obj, serializer)


async def async_decompress(
    compressed_data: Union[str, bytes],
    deserializer: Optional[Callable[[Union[str, bytes]], Any]] = None
) -> Any:
    """
    Async wrapper around `decompress()`. Offloads to a thread to avoid blocking the event loop.
    """
    return await asyncio.to_thread(decompress, compressed_data, deserializer)
