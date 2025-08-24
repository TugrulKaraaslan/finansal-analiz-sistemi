from __future__ import annotations

import pandas as pd

from backtest.naming.aliases import normalize_token
from backtest.naming.normalize import normalize_dataframe_columns


def canonical_name(name: str) -> str:
    return normalize_token(name)


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    norm_map = normalize_dataframe_columns(df.columns)
    return df.rename(columns=norm_map)


def canonicalize_filter_token(token: str) -> str:
    return normalize_token(token)


def set_name_normalization(mode: str) -> None:
    # compatibility no-op
    _ = mode
    return None


__all__ = [
    "canonical_name",
    "canonicalize_columns",
    "canonicalize_filter_token",
    "set_name_normalization",
]
