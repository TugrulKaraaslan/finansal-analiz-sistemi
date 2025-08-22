from __future__ import annotations

import pandas as pd


def _as_series(df: pd.DataFrame, name: str) -> pd.Series:
    return df[name]


def make_crossup(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a.shift(1) <= b.shift(1)) & (a > b)


def make_crossdown(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a.shift(1) >= b.shift(1)) & (a < b)


__all__ = ["_as_series", "make_crossup", "make_crossdown"]
