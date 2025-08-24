"""Path utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union


def resolve_path(path: Union[str, os.PathLike, bytes]) -> Path:
    """Expand user home (``~``) and environment variables safely.

    ``os.fspath`` is used instead of a manual ``isinstance`` check so that
    ``os.PathLike`` objects *and* ``bytes`` instances are accepted.  The
    built-in ``os.fspath`` helper mirrors the behaviour of functions in the
    standard library by converting any path-like object to a string (or raising
    ``TypeError`` for unsupported types).

    Parameters
    ----------
    path:
        Raw path as string, ``bytes`` or ``os.PathLike``.

    Returns
    -------
    pathlib.Path
        Normalized path with user and environment variables expanded.
    """

    try:
        raw = os.fspath(path)
    except TypeError as exc:
        raise TypeError("path must be str, bytes or Path-like") from exc

    # ``expandvars`` works on strings; ensure any ``bytes`` input is decoded
    # using the file system encoding via ``os.fsdecode``.
    raw_str = os.fsdecode(raw)

    # Perform environment and user expansion before creating ``Path``
    expanded = os.path.expandvars(raw_str)
    expanded = os.path.expanduser(expanded)
    return Path(expanded).resolve()


__all__ = ["resolve_path"]
