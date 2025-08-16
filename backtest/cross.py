import logging
import pandas as pd

logger = logging.getLogger(__name__)

def _shift(df: pd.DataFrame, col: str, n: int = 1) -> pd.Series:
    return df[col].shift(n)

def _missing(df: pd.DataFrame, cols: list[str]) -> list[str]:
    miss = [c for c in cols if c not in df.columns]
    for m in miss:
        logger.info("skip %s", m)
    return miss

def cross_up(df: pd.DataFrame, a: str, b: str) -> pd.Series:
    if _missing(df, [a, b]):
        return pd.Series(False, index=df.index)
    prev = _shift(df, a) <= _shift(df, b)
    now = df[a] > df[b]
    return prev & now

def cross_down(df: pd.DataFrame, a: str, b: str) -> pd.Series:
    if _missing(df, [a, b]):
        return pd.Series(False, index=df.index)
    prev = _shift(df, a) >= _shift(df, b)
    now = df[a] < df[b]
    return prev & now

def cross_over_level(df: pd.DataFrame, a: str, level: float) -> pd.Series:
    if _missing(df, [a]):
        return pd.Series(False, index=df.index)
    prev = _shift(df, a) <= level
    now = df[a] > level
    return prev & now

def cross_under_level(df: pd.DataFrame, a: str, level: float) -> pd.Series:
    if _missing(df, [a]):
        return pd.Series(False, index=df.index)
    prev = _shift(df, a) >= level
    now = df[a] < level
    return prev & now

__all__ = [
    "cross_up",
    "cross_down",
    "cross_over_level",
    "cross_under_level",
]
