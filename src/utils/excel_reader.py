"""Read Excel workbooks using a lightweight cache.

The cache avoids reloading unchanged files by tracking modification time.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd

# Global cache mapping absolute file paths to their modification time and the
# corresponding ``ExcelFile`` object. This ensures stale files are reloaded when
# the underlying Excel workbook changes on disk.
_excel_cache: Dict[str, tuple[float, pd.ExcelFile]] = {}


def clear_cache() -> None:
    """Clear the internal ExcelFile cache and close workbooks."""
    for _, xls in _excel_cache.values():
        try:
            xls.close()
        except Exception:
            pass
    _excel_cache.clear()


def open_excel_cached(path: str | os.PathLike[str], **kwargs: Any) -> pd.ExcelFile:
    """Return a cached ``ExcelFile`` object for the given path.

    The cache automatically refreshes if the file's modification time changes.
    """
    abs_path = os.path.abspath(os.fspath(path))
    mtime = os.path.getmtime(abs_path)
    cached = _excel_cache.get(abs_path)
    if cached is None or cached[0] != mtime:
        if cached is not None:
            try:
                cached[1].close()
            except Exception:
                pass
        _excel_cache[abs_path] = (mtime, pd.ExcelFile(abs_path, **kwargs))
    return _excel_cache[abs_path][1]


def read_excel_cached(
    path: str | os.PathLike[str], sheet_name: str, **kwargs: Any
) -> pd.DataFrame:
    """Parse ``sheet_name`` from a cached Excel workbook."""
    xls = open_excel_cached(path)
    return xls.parse(sheet_name=sheet_name, **kwargs)
