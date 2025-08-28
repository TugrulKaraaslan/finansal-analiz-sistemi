from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from time import perf_counter
from typing import Dict, List, Tuple

import pandas as pd

from backtest.batch.io import OutputWriter
from backtest.batch.scheduler import trading_days
from backtest.filters.engine import evaluate
from backtest.indicators.precompute import (
    collect_required_indicators,
    precompute_for_chunk,
)
from backtest.logging_conf import get_logger, log_with
from backtest.normalize import normalize_dataframe

log = get_logger("runner")


def _parse_symbol_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Map symbols to their column names.

    Column convention: SYMBOL_field. Falls back to df.attrs['symbol'] for
    single-symbol data.
    """
    sym_map: Dict[str, List[str]] = {}
    for c in df.columns:
        if isinstance(c, str) and "_" in c:
            sym, rest = c.split("_", 1)
            if sym.isupper():
                sym_map.setdefault(sym, []).append(c)
    if sym_map:
        return sym_map
    sym = df.attrs.get("symbol")
    if not sym:
        raise ValueError("df.attrs['symbol'] missing for single-symbol data")
    return {sym: list(df.columns)}


def _process_chunk(args):
    df_chunk, filters_df, indicators, day, alias_csv = args
    df_chunk, _ = normalize_dataframe(df_chunk, alias_csv, policy="prefer_first")  # noqa: E501
    df_chunk = precompute_for_chunk(df_chunk, indicators)
    d = pd.to_datetime(day)
    rows: List[Tuple[str, str]] = []
    sym_cols = _parse_symbol_columns(df_chunk)
    for sym, cols in sym_cols.items():
        sub = df_chunk[cols].copy()
        sub.columns = [c.split("_", 1)[1] if c.startswith(f"{sym}_") else c for c in cols]
        for i, r in enumerate(filters_df.itertuples(index=False)):
            code = str(r.FilterCode).strip()
            expr = str(r.PythonQuery).strip()
            log_with(
                log,
                "DEBUG",
                "evaluate",
                expr=expr,
                chunk_idx=i,
                symbol=sym,
            )
            try:
                mask = evaluate(sub, expr)
            except Exception as e:
                log.exception(
                    "evaluate failed",
                    extra={"extra_fields": {"expr": expr}},
                )
                raise ValueError(f"Filter evaluation failed: {expr} → {e}") from e  # noqa: E501
            val = mask.loc[d]
            ok = val.any() if isinstance(val, pd.Series) else bool(val)
            if ok:
                rows.append((sym, code))
    return rows


def run_scan_day(
    df: pd.DataFrame,
    day: str,
    filters_df: pd.DataFrame,
    *,
    alias_csv: str | None = None,
) -> List[Tuple[str, str]]:
    """Generate signals for a single day."""
    indicators = collect_required_indicators(filters_df)
    return _process_chunk(
        (
            df.copy(),
            filters_df,
            indicators,
            day,
            alias_csv,
        )
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
    """Run scans for a date range with optional symbol chunking and
    parallelism."""
    writer = OutputWriter(out_dir)
    days = trading_days(df.index, start, end)
    if len(days) == 0:
        raise RuntimeError("BR002: tarih aralığı veriyle kesişmiyor")

    sym_cols = _parse_symbol_columns(df)
    symbols = sorted(sym_cols.keys())
    chunks = [symbols[i : i + chunk_size] for i in range(0, len(symbols), chunk_size)]  # noqa: E203
    indicators = collect_required_indicators(filters_df)

    for day in days:
        t0 = perf_counter()
        tasks = []
        for chunk_syms in chunks:
            cols: List[str] = []
            for sym in chunk_syms:
                cols.extend(sym_cols[sym])
            df_chunk = df.loc[:, cols].copy()
            tasks.append(
                (
                    df_chunk,
                    filters_df,
                    indicators,
                    str(day.date()),
                    alias_csv,
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
        log.info(
            "DAY %s: IO+INDICATORS+FILTERS+WRITE took %.3fs",
            day,
            perf_counter() - t0,
        )


# trade DataFrame üretiliyorsa, maliyeti uygula (opsiyonel)
try:
    import os
    from pathlib import Path

    from backtest.portfolio.costs import CostParams, apply_costs

    _cost_cfg = Path(os.environ.get("COSTS_CFG", "config/costs.yaml"))
    _params = CostParams.from_yaml(_cost_cfg)
    _trades = globals().get("trades")
    if isinstance(_trades, pd.DataFrame) and not _trades.empty:
        trades = apply_costs(_trades, _params)
except Exception:
    # güvenli: maliyet katmanı optional, hatada akışı bozma
    pass
