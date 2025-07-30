"""Mixin class providing compression functionality."""
from typing import Any, Callable, Optional
from .compression import compress as _compress, decompress as _decompress
from .compression import async_compress as _async_compress, async_decompress as _async_decompress


class CompressorMixin:
    """Mixin class that provides compression and decompression capabilities.

    This mixin can be used by any class that needs to compress/decompress data
    with optional custom serialization/deserialization.

    Examples:
        >>> class MyHandler(CompressorMixin):
        ...     def process_data(self, data):
        ...         compressed = self.compress(data)
        ...         # ... do something with compressed data ...
        ...         return self.decompress(compressed)
    """

    def compress(
        self,
        obj: Any,
        serializer: Optional[Callable[[Any], str | bytes]] = None
    ) -> bytes:
        """Compress the given object into a compressed bytes object.
        The compression is done using zlib.

        Args:
            obj (Any): The object to compress and encode.
            serializer (Optional[Callable[[Any], str | bytes]]): Custom serializer function.
                If None, uses orjson.dumps. Defaults to None.

        Returns:
            str: The compressed and base64-encoded string.

        Examples:
            >>> handler.compress({"foo": "bar"}) # Basic compression
            >>> handler.compress(user, custom_user_serializer) # Custom serializer
        """
        return _compress(obj, serializer)

    def decompress(
        self,
        compressed_encoded_obj: str | bytes,
        deserializer: Optional[Callable[[str | bytes], Any]] = None
    ) -> Any:
        """Decompress the given compressed and encoded object into the original object.
        The decompression is done using zlib.

        Args:
            compressed_encoded_obj (str | bytes): The compressed and encoded bytes object (base64).
            deserializer (Optional[Callable[[str | bytes], Any]]): Custom deserializer function.
                If None, uses orjson.loads. Defaults to None.

        Returns:
            Any: The original object.

        Examples:
            >>> handler.decompress(compressed_str) # Basic decompression
            >>> handler.decompress(compressed_str, custom_user_deserializer) # Custom deserializer
        """
        return _decompress(compressed_encoded_obj, deserializer)

    async def async_compress(
        self,
        obj: Any,
        serializer: Optional[Callable[[Any], str | bytes]] = None
    ) -> str | bytes:
        """Async wrapper around `compress()`."""
        return await _async_compress(obj, serializer)

    async def async_decompress(
        self,
        compressed_encoded_obj: str | bytes,
        deserializer: Optional[Callable[[str | bytes], Any]] = None
    ) -> Any:
        """Async wrapper around `decompress()`."""
        return await _async_decompress(compressed_encoded_obj, deserializer)
