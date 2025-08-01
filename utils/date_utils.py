"""Utilities for robust date parsing.

The :func:`parse_date` helper converts diverse date values into
``pandas.Timestamp`` objects without raising ``ValueError``. Supported
inputs include strings, ``datetime`` objects, numeric representations and
``numpy.datetime64`` instances. Common invalid strings such as ``"NaN"``
or ``"None"`` are treated as missing and converted to ``pd.NaT``.
"""

from __future__ import annotations

__all__ = ["parse_date"]

from datetime import date, datetime

import numpy as np
import pandas as pd
from dateutil import parser
from pandas._libs.tslibs.nattype import NaTType

# Common explicit date formats tried before falling back to ``dateutil``.
_EXPLICIT_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%Y.%m.%d",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d/%m/%Y",
)


def parse_date(
    date_str: str | datetime | date | int | float | np.datetime64 | None,
) -> pd.Timestamp | NaTType:
    """Parse ``date_str`` into a :class:`pandas.Timestamp` or ``pd.NaT``.

    The function tries common ISO and day-first patterns first
    (``YYYY-MM-DD``, ``DD.MM.YYYY``, ``DD-MM-YYYY``, ``YYYY/MM/DD`` and
    ``DD/MM/YYYY``)
    and also understands pure digit forms like ``YYYYMMDD`` or ``DDMMYYYY``.
    If those attempts fail it falls back to a day-first parse via
    :mod:`dateutil`. Invalid inputs yield ``pd.NaT`` instead of raising
    ``ValueError``.

        Args:
            date_str (str | datetime | date | int | float | np.datetime64 | None):
                Date value to parse.

        Returns:
            pd.Timestamp | NaTType: Parsed timestamp or ``pd.NaT`` when parsing
            fails.
    """
    if isinstance(date_str, (datetime, date)):
        return pd.Timestamp(date_str)

    if isinstance(date_str, np.datetime64):
        return pd.to_datetime(date_str)

    # Normalize value to a stripped string for further checks
    if pd.isna(date_str):
        return pd.NaT

    if isinstance(date_str, float) and date_str.is_integer():
        value = str(int(date_str))
    else:
        value = str(date_str).strip()
        if value.lower() in {"nan", "none", "null"}:
            return pd.NaT
    if not value:
        return pd.NaT

    # Try explicit formats before falling back to dateutil
    for fmt in _EXPLICIT_FORMATS:
        ts = pd.to_datetime(value, format=fmt, errors="coerce")
        if pd.notna(ts):
            return ts

    if value.isdigit():
        if len(value) == 8:
            year = int(value[:4])
            if 1900 <= year <= 2100:
                ts = pd.to_datetime(value, format="%Y%m%d", errors="coerce")
            else:
                ts = pd.to_datetime(value, format="%d%m%Y", errors="coerce")
            if pd.notna(ts):
                return ts
        elif len(value) == 6:
            first = int(value[:2])
            if first > 12:
                ts = pd.to_datetime(value, format="%y%m%d", errors="coerce")
            else:
                ts = pd.to_datetime(value, format="%d%m%y", errors="coerce")
            if pd.notna(ts):
                return ts
        else:
            return pd.NaT

    # Generic day-first parsing with coercion (handles 07/03/25 etc.)
    ts = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.notna(ts):
        return ts

    # Fallback to dateutil for other variants
    try:
        return pd.Timestamp(parser.parse(value, dayfirst=True))
    except Exception:
        return pd.NaT
