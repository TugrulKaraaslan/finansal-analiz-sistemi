"""Utility helpers for the ``finansal`` package.

This module exposes :func:`lazy_chunk` for chunking iterables and
:func:`safe_set` for dtype-safe DataFrame assignment.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Generator, Sequence, TypeVar

from .dtypes import safe_set

T = TypeVar("T")


def lazy_chunk(seq: Iterable[T], size: int) -> Generator[Sequence[T], None, None]:
    """Yield ``seq`` in chunks of ``size`` without loading everything.

    Parameters
    ----------
    seq : Iterable[T]
        Source sequence to iterate over.
    size : int
        Number of items per chunk; must be positive.

    Yields
    ------
    Sequence[T]
        Consecutive chunks from the input sequence.

    """
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
