"""Read Excel workbooks with a simple in-memory cache.

Workbooks are indexed by absolute path and modification time. Cached
entries refresh automatically whenever the underlying file changes.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd

# Cache ``ExcelFile`` objects keyed by path and modification time. The cache
# refreshes automatically when the workbook on disk changes.


@dataclass
class ExcelCacheEntry:
    """Metadata for a cached workbook."""

    mtime: float
    book: pd.ExcelFile


logger = logging.getLogger(__name__)

_excel_cache: Dict[str, ExcelCacheEntry] = {}


def clear_cache() -> None:
    """Clear the in-memory ``ExcelFile`` cache and close open workbooks."""
    for entry in _excel_cache.values():
        try:
            entry.book.close()
        except Exception as exc:  # pragma: no cover - best effort cleanup
            logger.warning("Çalışma kitabı kapatılamadı: %s", exc)
    _excel_cache.clear()


def open_excel_cached(path: str | os.PathLike[str], **kwargs: Any) -> pd.ExcelFile:
    """Return a cached ``ExcelFile`` instance for ``path``.

    The cache automatically refreshes whenever the file on disk changes.

    Args:
        path (str | os.PathLike[str]): Excel file path.
        **kwargs: Additional arguments forwarded to :class:`pandas.ExcelFile`.

    Returns:
        pd.ExcelFile: Cached workbook handle.
    """
    abs_path = os.path.abspath(os.fspath(path))
    mtime = os.path.getmtime(abs_path)
    cached = _excel_cache.get(abs_path)
    if cached is None or cached.mtime != mtime:
        if cached is not None:
            try:
                cached.book.close()
            except Exception as exc:  # pragma: no cover - best effort cleanup
                logger.warning("Önceki çalışma kitabı kapatılamadı: %s", exc)
        _excel_cache[abs_path] = ExcelCacheEntry(
            mtime, pd.ExcelFile(abs_path, **kwargs)
        )
    return _excel_cache[abs_path].book


def read_excel_cached(
    path: str | os.PathLike[str], sheet_name: str, **kwargs: Any
) -> pd.DataFrame:
    """Parse ``sheet_name`` from a cached Excel workbook.

    This is a thin wrapper around :func:`open_excel_cached`.

    Args:
        path (str | os.PathLike[str]): Excel file path.
        sheet_name (str): Worksheet name to parse.
        **kwargs: Additional arguments passed to :meth:`pandas.ExcelFile.parse`.

    Returns:
        pd.DataFrame: Data read from the worksheet.
    """
    xls = open_excel_cached(path)
    return xls.parse(sheet_name=sheet_name, **kwargs)
