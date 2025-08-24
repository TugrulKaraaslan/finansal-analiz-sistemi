from __future__ import annotations

from typing import Iterable

import pandas as pd


def trading_days(index: pd.DatetimeIndex, start: str, end: str) -> pd.DatetimeIndex:
    """Verilen tarih aralığında, veri indeksine göre işlem günlerini döndür.
    Tarihler ISO (YYYY-MM-DD) olabilir.
    """
    idx = pd.to_datetime(index).sort_values().unique()
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)
    days = idx[(idx >= s) & (idx <= e)]
    return pd.DatetimeIndex(days)
