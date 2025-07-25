"""Utility helpers for the ``src`` package.

Exports wrappers around :mod:`openpyxl`'s ``ExcelFile`` handling
implemented in :mod:`.excel_reader`.
"""

from __future__ import annotations

from . import excel_reader
from .excel_reader import clear_cache, open_excel_cached, read_excel_cached

__all__ = [
    "clear_cache",
    "excel_reader",
    "open_excel_cached",
    "read_excel_cached",
]
