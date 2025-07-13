"""Helpers for robust date parsing.

The :func:`parse_date` utility normalizes various date strings to
``pd.Timestamp`` objects without raising ``ValueError``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Union

import pandas as pd
from dateutil import parser
from pandas._libs.tslibs.nattype import NaTType


def parse_date(date_str: Union[str, datetime]) -> pd.Timestamp | NaTType:
    """Parse ``date_str`` into a timestamp.

    The function first attempts the ISO form ``YYYY-MM-DD`` followed by the
    Turkish/European style ``DD.MM.YYYY``. If both fail, a flexible day-first
    parse via :mod:`dateutil` is used. Invalid inputs yield ``pd.NaT`` instead
    of raising ``ValueError``.

    Args:
        date_str (Union[str, datetime]): Date string or datetime object to
            parse.

    Returns:
        pd.Timestamp | NaTType: Parsed timestamp or ``pd.NaT`` when parsing
        fails.
    """
    if pd.isna(date_str) or str(date_str).strip() == "":
        return pd.NaT

    # Try explicit ISO first
    ts = pd.to_datetime(date_str, format="%Y-%m-%d", errors="coerce")
    if ts is not pd.NaT:
        return ts

    # Try Turkish/European day.month.year
    ts = pd.to_datetime(date_str, format="%d.%m.%Y", errors="coerce")
    if ts is not pd.NaT:
        return ts

    # Generic day-first parsing with coercion (handles 07/03/25 etc.)
    ts = pd.to_datetime(date_str, dayfirst=True, errors="coerce")
    if ts is not pd.NaT:
        return ts

    # Fallback to dateutil for other variants
    try:
        return parser.parse(str(date_str), dayfirst=True)
    except Exception:
        return pd.NaT
