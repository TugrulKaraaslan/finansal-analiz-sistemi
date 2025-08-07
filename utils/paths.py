"""Path utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union


def resolve_path(path: Union[str, os.PathLike]) -> Path:
    """Expand user home (``~``) and environment variables safely.

    Parameters
    ----------
    path:
        Raw path as string or ``os.PathLike``.

    Returns
    -------
    pathlib.Path
        Normalized path with user and environment variables expanded.
    """

    if not isinstance(path, (str, os.PathLike)):
        raise TypeError("path must be str or Path-like")

    # ``expandvars`` must operate on string before converting to ``Path``
    expanded = os.path.expandvars(str(path))
    expanded = os.path.expanduser(expanded)
    return Path(expanded).resolve()


__all__ = ["resolve_path"]

