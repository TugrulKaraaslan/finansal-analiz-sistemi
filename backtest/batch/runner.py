from __future__ import annotations
import pandas as pd
from typing import Iterable, List, Tuple
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
import logging

from backtest.normalize import normalize_dataframe
from backtest.filters.engine import evaluate
from backtest.indicators.precompute import (
    collect_required_indicators,
    precompute_for_chunk,
)
from backtest.batch.scheduler import trading_days
from backtest.batch.io import OutputWriter

logger = logging.getLogger(__name__)


def _process_chunk(args):
    df_chunk, filters_df, indicators, day, alias_csv, multi_symbol = args
    df_chunk, _ = normalize_dataframe(df_chunk, alias_csv, policy="prefer_first")
    df_chunk = precompute_for_chunk(df_chunk, indicators)
    d = pd.to_datetime(day)
    rows: List[Tuple[str, str]] = []
    if multi_symbol:
        symbols = sorted({c[0] for c in df_chunk.columns})
        for sym in symbols:
            sub = df_chunk.xs(sym, axis=1, level=0)
            for _, r in filters_df.iterrows():
                code = str(r["FilterCode"]).strip()
                expr = str(r["PythonQuery"]).strip()
                try:
                    mask = evaluate(sub, expr)
                except Exception as e:
                    raise ValueError(f"Filter evaluation failed: {expr} → {e}") from e
                val = mask.loc[d]
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                if bool(val):
                    rows.append((sym, code))
    else:
        for _, r in filters_df.iterrows():
            code = str(r["FilterCode"]).strip()
            expr = str(r["PythonQuery"]).strip()
            try:
                mask = evaluate(df_chunk, expr)
            except Exception as e:
                raise ValueError(f"Filter evaluation failed: {expr} → {e}") from e
            val = mask.loc[d]
            if isinstance(val, pd.Series):
                val = val.iloc[0]
            if bool(val):
                rows.append(("SYMBOL", code))
    return rows


def run_scan_day(
    df: pd.DataFrame,
    day: str,
    filters_df: pd.DataFrame,
    *,
    alias_csv: str | None = None,
) -> List[Tuple[str, str]]:
    """Generate signals for a single day."""
    multi_symbol = isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2
    indicators = collect_required_indicators(filters_df)
    return _process_chunk(
        (df.copy(), filters_df, indicators, day, alias_csv, multi_symbol)
    )


def run_scan_range(
    df: pd.DataFrame,
    start: str,
    end: str,
    filters_df: pd.DataFrame,
    *,
    out_dir: str,
    alias_csv: str | None = None,
    parquet_cache: str | None = None,
    ind_cache: str | None = None,
    chunk_size: int = 20,
    workers: int = 1,
) -> None:
    """Run scans for a date range with optional symbol chunking and parallelism."""
    writer = OutputWriter(out_dir)
    days = trading_days(df.index, start, end)
    if len(days) == 0:
        raise RuntimeError("BR002: tarih aralığı veriyle kesişmiyor")

    multi_symbol = isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2
    symbols = sorted({c[0] for c in df.columns}) if multi_symbol else ["SYMBOL"]
    chunks = [symbols[i : i + chunk_size] for i in range(0, len(symbols), chunk_size)]
    indicators = collect_required_indicators(filters_df)

    for day in days:
        t0 = perf_counter()
        tasks = []
        for chunk_syms in chunks:
            if multi_symbol:
                df_chunk = df.loc[:, pd.IndexSlice[chunk_syms, :]].copy()
            else:
                df_chunk = df.copy()
            tasks.append(
                (
                    df_chunk,
                    filters_df,
                    indicators,
                    str(day.date()),
                    alias_csv,
                    multi_symbol,
                )
            )
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                results = ex.map(_process_chunk, tasks)
        else:
            results = map(_process_chunk, tasks)
        rows: List[Tuple[str, str]] = []
        for r in results:
            rows.extend(r)
        writer.write_day(day, rows)
        logger.info(
            "DAY %s: IO+INDICATORS+FILTERS+WRITE took %.3fs",
            day,
            perf_counter() - t0,
        )
