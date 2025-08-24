"""Path utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union


def resolve_path(path: Union[str, os.PathLike, bytes]) -> Path:
    """Resolve a path provided as ``str``, ``bytes`` or ``os.PathLike``.

    ``os.fspath`` mirrors the standard library behaviour and ensures a
    :class:`TypeError` is raised for unsupported objects instead of silently
    calling ``str()``.  ``bytes`` input is decoded with :func:`os.fsdecode` so
    that environment and user expansions operate on text.
    """

    try:
        raw = os.fspath(path)
    except TypeError as exc:  # pragma: no cover - defensive programming
        raise TypeError("path must be str, bytes or os.PathLike") from exc

    # ``expandvars`` operates on strings only; ``fsdecode`` handles ``bytes``
    # according to the OS file system encoding.
    raw_str = os.fsdecode(raw)

    # Expand environment variables then ``~`` before normalising with
    # :class:`pathlib.Path`.
    expanded = os.path.expandvars(raw_str)
    expanded = os.path.expanduser(expanded)
    return Path(expanded).resolve()


__all__ = ["resolve_path"]
