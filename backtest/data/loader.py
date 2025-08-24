from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from backtest.paths import DATA_DIR

from .backends import pandas_backend, polars_backend


def load_prices(
    symbols: Sequence[str],
    start: str | None = None,
    end: str | None = None,
    cols: Iterable[str] | None = None,
    backend: str = "pandas",
    parquet_dir: str | Path = DATA_DIR / "parquet",
):
    """Load price data for *symbols* between *start* and *end*.

    Parameters
    ----------
    symbols : sequence of str
        Symbols to load.
    start, end : str, optional
        Date bounds in YYYY-MM-DD format.
    cols : iterable of str, optional
        Desired columns; ``None`` loads all columns.
    backend : {"pandas", "polars"}
        Data backend to use.
    parquet_dir : str or Path
        Root directory containing ``symbol=`` partitions (default ``DATA_DIR/parquet``).
    """
    if backend == "polars":
        df = polars_backend.load_prices(parquet_dir, symbols, start, end, cols)
        return polars_backend.to_pandas(df)
    else:
        return pandas_backend.load_prices(parquet_dir, symbols, start, end, cols)
