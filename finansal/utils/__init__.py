"""Utility helpers for the ``finansal`` package."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Generator, Sequence, TypeVar

from .dtypes import safe_set

T = TypeVar("T")


def lazy_chunk(seq: Iterable[T], size: int) -> Generator[Sequence[T], None, None]:
    """Yield sequence chunks lazily without loading all into memory."""
    if size <= 0:
        raise ValueError("size must be positive")

    chunk: list[T] = []
    for item in seq:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


__all__ = ["lazy_chunk", "safe_set"]
