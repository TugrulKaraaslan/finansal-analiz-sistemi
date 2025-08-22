from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Callable

# Fonksiyon imzaları: tümü vektörel pandas.Series döndürür

def _ensure_series(x):
    if isinstance(x, (int, float)):
        return x  # skaler
    if isinstance(x, pd.Series):
        return x
    raise TypeError("Beklenen pandas.Series veya skaler")


def cross_up(a: pd.Series, b: pd.Series) -> pd.Series:
    a = _ensure_series(a); b = _ensure_series(b)
    prev = (a.shift(1) <= b.shift(1))
    now  = (a > b)
    out = prev & now
    out.iloc[-1] = False  # son gözlem teyitsiz
    return out.fillna(False)


def cross_down(a: pd.Series, b: pd.Series) -> pd.Series:
    a = _ensure_series(a); b = _ensure_series(b)
    prev = (a.shift(1) >= b.shift(1))
    now  = (a <= b)
    out = prev & now
    return out.fillna(False)

FUNCTIONS: Dict[str, Callable[..., pd.Series]] = {
    "cross_up": cross_up,
    "cross_down": cross_down,
}
