from __future__ import annotations

from __future__ import annotations

import pandas as pd

from backtest.naming import normalize_columns as _normalize_columns, normalize_name


def canonical_name(name: str) -> str:
    return normalize_name(name)


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normed, _ = _normalize_columns(df)
    return normed


def canonicalize_filter_token(token: str) -> str:
    return normalize_name(token)


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
