"""Utilities for robust date parsing.

The :func:`parse_date` helper converts diverse date strings to
``pd.Timestamp`` objects without raising ``ValueError``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Union

import pandas as pd
from dateutil import parser
from pandas._libs.tslibs.nattype import NaTType


def parse_date(date_str: Union[str, datetime]) -> pd.Timestamp | NaTType:
    """Parse ``date_str`` into a :class:`pandas.Timestamp` or ``pd.NaT``.

    The function tries ISO ``YYYY-MM-DD`` and ``DD.MM.YYYY`` formats first,
    then falls back to a day-first parse via :mod:`dateutil`. Invalid inputs
    yield ``pd.NaT`` instead of raising ``ValueError``.

    Args:
        date_str (Union[str, datetime]): Date string or datetime object to
            parse.

    Returns:
        pd.Timestamp | NaTType: Parsed timestamp or ``pd.NaT`` when parsing
        fails.
    """
    if pd.isna(date_str) or str(date_str).strip() == "":
        return pd.NaT

    # Short-circuit for already parsed dates
    if isinstance(date_str, datetime):
        return pd.Timestamp(date_str)

    # Try explicit formats before falling back to dateutil
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        ts = pd.to_datetime(date_str, format=fmt, errors="coerce")
        if ts is not pd.NaT:
            return ts

    if str(date_str).isdigit() and len(str(date_str)) == 8:
        ts = pd.to_datetime(date_str, format="%Y%m%d", errors="coerce")
        if ts is not pd.NaT:
            return ts

    # Generic day-first parsing with coercion (handles 07/03/25 etc.)
    ts = pd.to_datetime(date_str, dayfirst=True, errors="coerce")
    if ts is not pd.NaT:
        return ts

    # Fallback to dateutil for other variants
    try:
        return pd.Timestamp(parser.parse(str(date_str), dayfirst=True))
    except Exception:
        return pd.NaT
