from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd


def _read_symbol(path: Path, cols: Iterable[str] | None) -> pd.DataFrame:
    files = sorted(path.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files under {path}")
    df = pd.concat([pd.read_parquet(f, columns=cols) for f in files])
    return df


def load_prices(
    parquet_dir: str | Path,
    symbols: Sequence[str],
    start: str | None,
    end: str | None,
    cols: Iterable[str] | None,
) -> pd.DataFrame:
    root = Path(parquet_dir)
    frames = []
    for sym in symbols:
        p = root / f"symbol={sym}"
        df = _read_symbol(p, cols)
        if start:
            df = df[df["Date"] >= start]
        if end:
            df = df[df["Date"] <= end]
        df["Symbol"] = sym
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    return out
