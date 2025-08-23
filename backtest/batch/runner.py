from __future__ import annotations
import pandas as pd
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor
from time import perf_counter

from backtest.normalize import normalize_dataframe
from backtest.filters.engine import evaluate
from backtest.indicators.precompute import (
    collect_required_indicators,
    precompute_for_chunk,
)
from backtest.batch.scheduler import trading_days
from backtest.batch.io import OutputWriter
from backtest.logging_conf import get_logger, log_with

log = get_logger("runner")


def _process_chunk(args):
    df_chunk, filters_df, indicators, day, alias_csv, multi_symbol = args
    df_chunk, _ = normalize_dataframe(
        df_chunk, alias_csv, policy="prefer_first"
    )  # noqa: E501
    df_chunk = precompute_for_chunk(df_chunk, indicators)
    d = pd.to_datetime(day)
    rows: List[Tuple[str, str]] = []
    if multi_symbol:
        symbols = sorted({c[0] for c in df_chunk.columns})
        for sym in symbols:
            sub = df_chunk.xs(sym, axis=1, level=0)
            for i, r in enumerate(filters_df.itertuples(index=False)):
                code = str(r.FilterCode).strip()
                expr = str(r.PythonQuery).strip()
                log_with(log, "DEBUG", "evaluate", expr=expr, chunk_idx=i, symbol=sym)
                try:
                    mask = evaluate(sub, expr)
                except Exception as e:
                    log.exception("evaluate failed", extra={"extra_fields": {"expr": expr}})
                    raise ValueError(
                        f"Filter evaluation failed: {expr} → {e}"
                    ) from e  # noqa: E501
                if bool(mask.loc[d]):
                    rows.append((sym, code))
    else:
        for i, r in enumerate(filters_df.itertuples(index=False)):
            code = str(r.FilterCode).strip()
            expr = str(r.PythonQuery).strip()
            log_with(log, "DEBUG", "evaluate", expr=expr, chunk_idx=i)
            try:
                mask = evaluate(df_chunk, expr)
            except Exception as e:
                log.exception("evaluate failed", extra={"extra_fields": {"expr": expr}})
                raise ValueError(
                    f"Filter evaluation failed: {expr} → {e}"
                ) from e  # noqa: E501
            if bool(mask.loc[d]):
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
    multi_symbol = (
        isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2
    )  # noqa: E501
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
    """Run scans for a date range with optional symbol chunking and
    parallelism."""
    writer = OutputWriter(out_dir)
    days = trading_days(df.index, start, end)
    if len(days) == 0:
        raise RuntimeError("BR002: tarih aralığı veriyle kesişmiyor")

    multi_symbol = (
        isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2
    )  # noqa: E501
    symbols = (
        sorted({c[0] for c in df.columns}) if multi_symbol else ["SYMBOL"]
    )  # noqa: E501
    chunks = [  # noqa: E501
        symbols[i : i + chunk_size]  # noqa: E203
        for i in range(0, len(symbols), chunk_size)
    ]
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
        log.info(
            "DAY %s: IO+INDICATORS+FILTERS+WRITE took %.3fs",
            day,
            perf_counter() - t0,
        )


# trade DataFrame üretiliyorsa, maliyeti uygula (opsiyonel)
try:
    from backtest.portfolio.costs import CostParams, apply_costs
    from pathlib import Path
    import os

    _cost_cfg = Path(os.environ.get("COSTS_CFG", "config/costs.yaml"))
    _params = CostParams.from_yaml(_cost_cfg)
    _trades = globals().get("trades")
    if isinstance(_trades, pd.DataFrame) and not _trades.empty:
        trades = apply_costs(_trades, _params)
except Exception:
    # güvenli: maliyet katmanı optional, hatada akışı bozma
    pass
