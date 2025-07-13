"""Read Excel workbooks using a lightweight cache.

Opened workbooks are stored in a process-level dictionary keyed by their
absolute path and modification time. Entries automatically refresh when the
file changes on disk so repeated reads remain efficient.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd

# Cache ``ExcelFile`` objects keyed by path and modification time. The cache
# refreshes automatically when the workbook on disk changes.
_excel_cache: Dict[str, tuple[float, pd.ExcelFile]] = {}


def clear_cache() -> None:
    """Clear the internal ``ExcelFile`` cache and close workbooks."""
    for _, xls in _excel_cache.values():
        try:
            xls.close()
        except Exception:
            pass
    _excel_cache.clear()


def open_excel_cached(path: str | os.PathLike[str], **kwargs: Any) -> pd.ExcelFile:
    """Return a cached ``ExcelFile`` instance for ``path``.

    The cache automatically refreshes when the underlying file changes.

    Args:
        path (str | os.PathLike[str]): Excel file path.
        **kwargs: Additional arguments forwarded to :class:`pandas.ExcelFile`.

    Returns:
        pd.ExcelFile: Cached workbook handle.
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
    """Parse ``sheet_name`` from a cached Excel workbook.

    Args:
        path (str | os.PathLike[str]): Excel file path.
        sheet_name (str): Worksheet name to parse.
        **kwargs: Additional arguments passed to :meth:`pandas.ExcelFile.parse`.

    Returns:
        pd.DataFrame: Data read from the worksheet.
    """
    xls = open_excel_cached(path)
    return xls.parse(sheet_name=sheet_name, **kwargs)
