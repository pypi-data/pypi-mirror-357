"""Serialization utilities for ValiotWorkflows.

This module provides utilities for serializing and deserializing objects,
including dataclasses.

It uses orjson for serialization and deserialization.

It also provides utilities for building smart serializer and deserializer functions,
receiving a dictionary of models and their corresponding dataclasses.

These serializers and deserializers are cycle-safe, meaning they can handle
cyclic relationships between objects.

This is useful for compressing and decompressing objects,
as well as for sending objects between services,
and for storing objects in a database (e.g. Redis, S3, etc.).

"""
from typing import Any, Callable, Union, Type
from dataclasses import fields
import asyncio
from typing import Any, Awaitable, Callable, Type, Set, Union
import dataclasses
from dataclasses import fields, is_dataclass
import orjson


def build_serializer(models: dict[str, Type], id_attr: str = "id") -> Callable[[Any], str]:
    """Build a serializer function for the given dataclass models."""
    # Reverse lookup: class -> name
    class_to_name = {cls: name for name, cls in models.items()}

    def _to_serializable(obj: Any, seen: Set[int]) -> Any:
        # 1) If this is any dataclass instance...
        if is_dataclass(obj):
            cls = type(obj)
            # 1a) If its class isn’t in our models, error out immediately:
            if cls not in class_to_name:
                raise KeyError(
                    f"Missing model definition for '{cls.__name__}'")

            oid = id(obj)
            # 1b) Cycle detection for known models:
            if oid in seen:
                # Just emit a reference by type+id_attr
                return {"__type__": class_to_name[cls], id_attr: getattr(obj, id_attr)}

            seen.add(oid)
            # 1c) “Unroll” the dataclass fields
            data = {"__type__": class_to_name[cls]}
            for f in fields(obj):
                data[f.name] = _to_serializable(getattr(obj, f.name), seen)
            return data

        # 2) Regular dict/list/tuple handling
        if isinstance(obj, dict):
            return {k: _to_serializable(v, seen) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_to_serializable(v, seen) for v in obj]

        # 3) Primitive fallback
        return obj

    def serializer(obj: Any) -> str:
        serializable = _to_serializable(obj, set())
        return orjson.dumps(serializable).decode("utf-8")

    return serializer


def build_deserializer(models: dict[str, Type], id_attr: str = "id") -> Callable[[Union[str, bytes]], Any]:
    """
    Build a deserializer function for the given dataclass models.
    Now skips 'id_attr' in the required‐field validation so that
    simple objects (no cycles) deserialize without error.
    """
    name_to_class = models

    def deserializer(json_input: Union[str, bytes]) -> Any:
        raw_data = orjson.loads(json_input.decode(
            "utf-8")) if isinstance(json_input, bytes) else orjson.loads(json_input)
        refs: dict[tuple[str, Any], Any] = {}

        def _from_serializable(node: Any) -> Any:
            if isinstance(node, dict) and "__type__" in node:
                tname = node["__type__"]
                if tname not in name_to_class:
                    raise KeyError(f"Unknown model type '{tname}' in payload")
                cls = name_to_class[tname]
                identifier = node.get(id_attr)

                # Cycle check: if we've seen (tname, id) before, return it
                if identifier is not None and (tname, identifier) in refs:
                    return refs[(tname, identifier)]

                # 1) Compute which fields are truly “required” (init=True,
                #    no default/default_factory) but SKIP id_attr itself.
                required_fields = [
                    f.name
                    for f in fields(cls)
                    if (
                        f.init
                        and f.default is dataclasses.MISSING
                        and f.default_factory is dataclasses.MISSING
                        and f.name != id_attr
                    )
                ]

                # 2) Check what keys JSON actually provided (excluding __type__ and id_attr)
                present_keys = set(node.keys()) - {"__type__", id_attr}

                missing = [
                    name for name in required_fields if name not in present_keys]
                if missing:
                    raise KeyError(
                        f"Missing field(s) {missing!r} for model '{tname}'")

                # 3) Make a blank instance, register it for cycles, then populate
                inst = cls.__new__(cls)  # type: ignore[call-arg]
                if identifier is not None:
                    refs[(tname, identifier)] = inst

                for k, v in node.items():
                    if k == "__type__":
                        continue
                    setattr(inst, k, _from_serializable(v))
                return inst

            # Plain dict/list or primitive
            if isinstance(node, dict):
                return {k: _from_serializable(v) for k, v in node.items()}
            if isinstance(node, list):
                return [_from_serializable(v) for v in node]
            return node

        return _from_serializable(raw_data)

    return deserializer


def build_async_serializer(
    models: dict[str, Type], id_attr: str = "id"
) -> Callable[[Any], Awaitable[str]]:
    """An async wrapper around build_serializer."""
    sync_serializer = build_serializer(models, id_attr)

    async def serializer(obj: Any) -> str:
        loop = asyncio.get_running_loop()
        # offload to default ThreadPoolExecutor
        return await loop.run_in_executor(None, sync_serializer, obj)

    return serializer


def build_async_deserializer(
    models: dict[str, Type], id_attr: str = "id"
) -> Callable[[Union[str, bytes]], Awaitable[Any]]:
    """An async wrapper around build_deserializer."""
    sync_deserializer = build_deserializer(models, id_attr)

    async def deserializer(json_input: Union[str, bytes]) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, sync_deserializer, json_input)

    return deserializer
