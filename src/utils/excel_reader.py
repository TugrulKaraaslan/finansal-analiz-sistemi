"""Excel reading utilities with simple caching."""

from __future__ import annotations

import os
from typing import Any, Dict

import pandas as pd

# Global cache mapping absolute file paths to ``ExcelFile`` objects
_excel_cache: Dict[str, pd.ExcelFile] = {}


def open_excel_cached(path: str, **kwargs: Any) -> pd.ExcelFile:
    """Return a cached ``ExcelFile`` object for the given path."""
    abs_path = os.path.abspath(os.fspath(path))
    if abs_path not in _excel_cache:
        _excel_cache[abs_path] = pd.ExcelFile(abs_path, **kwargs)
    return _excel_cache[abs_path]


def read_excel_cached(path: str, sheet_name: str, **kwargs: Any) -> pd.DataFrame:
    """Parse ``sheet_name`` from a cached Excel workbook."""
    xls = open_excel_cached(path)
    return xls.parse(sheet_name=sheet_name, **kwargs)


def clear_cache() -> None:
    """Clear the internal ExcelFile cache and close workbooks."""
    for xls in _excel_cache.values():
        try:
            xls.close()
        except Exception:
            pass
    _excel_cache.clear()
