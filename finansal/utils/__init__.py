"""Utility helpers for the ``finansal`` package.

This module exposes :func:`lazy_chunk` to iterate over sequences in fixed-size
chunks and :func:`safe_set` for dtype-safe DataFrame assignment.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Sequence, TypeVar

from .dtypes import safe_set

T = TypeVar("T")


def lazy_chunk(seq: Iterable[T], size: int) -> Iterator[Sequence[T]]:
    """Yield ``seq`` in immutable chunks of ``size``.

    Args:
        seq (Iterable[T]): Source sequence to iterate over.
        size (int): Number of items per chunk; must be positive.

    Yields:
        Sequence[T]: Consecutive tuples from the input sequence.

    """
    if size <= 0:
        raise ValueError("size must be positive")

    iterator = iter(seq)
    while True:
        chunk = tuple(islice(iterator, size))
        if not chunk:
            break
        yield chunk


__all__ = ["lazy_chunk", "safe_set"]
