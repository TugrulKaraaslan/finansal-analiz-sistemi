"""Utilities for safely parsing dates without raising errors.

The :func:`parse_date` helper normalizes various date strings to
``pd.Timestamp`` objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Union

import pandas as pd
from dateutil import parser
from pandas._libs.tslibs.nattype import NaTType


def parse_date(date_str: Union[str, datetime]) -> pd.Timestamp | NaTType:
    """Return a parsed timestamp or ``pd.NaT`` on failure.

    The parser tries ``YYYY-MM-DD`` first, then ``DD.MM.YYYY`` and finally a
    generic day-first parse before falling back to :mod:`dateutil`. Any invalid
    input yields ``pd.NaT`` instead of raising ``ValueError``.
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
