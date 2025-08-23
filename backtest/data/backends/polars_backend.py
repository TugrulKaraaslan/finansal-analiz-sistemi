from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence
from datetime import datetime

import polars as pl


def _scan_symbol(path: Path, cols: Iterable[str] | None) -> pl.LazyFrame:
    files = sorted(path.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files under {path}")
    lf = pl.scan_parquet([str(f) for f in files])
    if cols is not None:
        lf = lf.select(list(cols))
    return lf


def load_prices(
    parquet_dir: str | Path,
    symbols: Sequence[str],
    start: str | None,
    end: str | None,
    cols: Iterable[str] | None,
) -> pl.DataFrame:
    root = Path(parquet_dir)
    lfs = []
    start_dt = datetime.strptime(start, "%Y-%m-%d") if start else None
    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else None
    for sym in symbols:
        p = root / f"symbol={sym}"
        lf = _scan_symbol(p, cols)
        if start_dt:
            lf = lf.filter(pl.col("Date") >= start_dt)
        if end_dt:
            lf = lf.filter(pl.col("Date") <= end_dt)
        lf = lf.with_columns(pl.lit(sym).alias("Symbol"))
        lfs.append(lf)
    lazy = pl.concat(lfs)
    return lazy.collect()


def to_pandas(df: pl.DataFrame):
    return df.to_pandas()


def concat_symbols_lazy(symbol_frames: Sequence[pl.LazyFrame]) -> pl.LazyFrame:
    return pl.concat(symbol_frames)


def ensure_monotonic(df: pl.DataFrame, column: str = "Date") -> pl.DataFrame:
    return df.sort(column)
