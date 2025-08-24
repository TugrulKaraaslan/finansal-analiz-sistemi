from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def collect_required_indicators(filters_df: pd.DataFrame) -> set[str]:
    """Extract indicator tokens used in filter expressions.

    This is a very small string scanner and does not attempt to fully parse the
    expression. It is sufficient for simple demo use cases.
    """
    out: set[str] = set()
    for expr in filters_df.get("PythonQuery", []).astype(str):
        for token in ["sma", "ema", "rsi", "adx", "macd", "boll"]:
            if token in expr:
                out.add(token)
    return out


def precompute_for_chunk(
    df_chunk: pd.DataFrame,
    indicators: set[str],
    cache_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Compute a small subset of indicators for a dataframe chunk.

    Only a handful of indicators are supported and the implementation avoids
    heavy third‑party dependencies such as TA‑Lib or pandas_ta. The calculations
    are vectorised via pandas/numpy primitives.
    """
    out = df_chunk.copy()
    if "sma" in indicators:
        out["sma_20"] = out["close"].rolling(20).mean()
    if "ema" in indicators:
        out["ema_20"] = out["close"].ewm(span=20).mean()
    if "rsi" in indicators:
        delta = out["close"].diff()
        up = delta.clip(lower=0).ewm(alpha=1 / 14).mean()
        down = -delta.clip(upper=0).ewm(alpha=1 / 14).mean()
        rs = up / down
        out["rsi_14"] = 100 - (100 / (1 + rs))
    if cache_dir:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        key = "chunk" + str(hash(frozenset(indicators)))
        out.to_parquet(cache_dir / f"{key}.parquet")
    return out
