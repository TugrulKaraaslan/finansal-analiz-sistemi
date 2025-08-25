from __future__ import annotations

import json
import re
import time
import warnings
from pathlib import Path

import pandas as pd
from loguru import logger

from backtest.columns import canonical_map
from backtest.filters import engine as filter_engine
from backtest.filters.engine import evaluate


def _to_pandas_ops(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


def _eval_expr(df: pd.DataFrame, expr: str) -> pd.Series:
    return evaluate(df, expr)


UNSAFE_EVAL = False
_EVENTS_FILE = Path("events.jsonl")
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _log_event(event: dict) -> None:
    with _EVENTS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def run_screener(
    df_ind: pd.DataFrame,
    filters_df: pd.DataFrame,
    date,
    stop_on_filter_error: bool = False,
    raise_on_error: bool = True,
) -> pd.DataFrame:
    if not isinstance(df_ind, pd.DataFrame):
        raise TypeError("df_ind must be a DataFrame")
    if not isinstance(filters_df, pd.DataFrame):
        raise TypeError("filters_df must be a DataFrame")
    if df_ind.empty:
        logger.error("df_ind is empty")
        raise ValueError("df_ind is empty")
    if filters_df.empty:
        logger.error("filters_df is empty")
        raise ValueError("filters_df is empty")

    df_ind = df_ind.copy()
    colmap = canonical_map(df_ind.columns)
    for canon, original in colmap.items():
        if canon != original and canon not in df_ind.columns:
            df_ind[canon] = df_ind[original]

    req_df = {"symbol", "date", "open", "high", "low", "close", "volume"}
    missing_df = req_df.difference(df_ind.columns)
    if missing_df:
        msg = f"df_ind missing columns: {', '.join(sorted(missing_df))}"
        logger.error(msg)
        raise ValueError(msg)
    if not {"FilterCode", "PythonQuery"}.issubset(filters_df.columns):
        msg = "filters_df missing required columns"
        logger.error(msg)
        raise ValueError(msg)

    df_ind["date"] = pd.to_datetime(df_ind["date"]).dt.normalize()

    def _empty_output() -> pd.DataFrame:
        cols = ["FilterCode"]
        if "Group" in filters_df.columns:
            cols.append("Group")
        cols.append("Symbol")
        if "Side" in filters_df.columns:
            cols.append("Side")
        cols.append("Date")
        data = {c: pd.Series(dtype=object) for c in cols}
        return pd.DataFrame(data, columns=cols)

    day = pd.to_datetime(date).normalize()
    d = df_ind[df_ind["date"] == day].copy()
    if d.empty:
        logger.warning("No data for date {day}", day=day)
        return _empty_output()
    d = d.reset_index(drop=True)
    filters_df = filters_df.copy()
    dups = filters_df["FilterCode"].duplicated()
    if dups.any():
        dup_codes = filters_df.loc[dups, "FilterCode"].tolist()
        raise ValueError(f"Duplicate FilterCode detected: {dup_codes}")
    filters_df["FilterCode"] = filters_df["FilterCode"].astype(str).str.strip()
    filters_df["expr"] = filters_df["PythonQuery"].astype(str).map(_to_pandas_ops)
    groups = filters_df.get("Group")
    if groups is None:
        groups = [None] * len(filters_df)
    sides = filters_df.get("Side")
    if sides is None:
        sides = [None] * len(filters_df)
    out_frames = []
    missing_cols_total: set[str] = set()
    for code, expr, grp, side in zip(filters_df["FilterCode"], filters_df["expr"], groups, sides):
        t0 = time.perf_counter()
        skipped = False
        reason: str | None = None
        hits = 0
        side_norm = None
        if pd.notna(side) and str(side).strip():
            side_norm = str(side).strip().lower()
            if side_norm not in {"long", "short"}:
                msg = f"Filter {code!r} has invalid Side {side!r}"
                if stop_on_filter_error:
                    logger.error("Filter invalid Side", code=code, side=side)
                    raise ValueError(msg)
                logger.warning("Filter skipped due to invalid Side", code=code, side=side)
                skipped = True
                reason = "INVALID_SIDE"
                dt = int((time.perf_counter() - t0) * 1000)
                _log_event(
                    {
                        "event": "FILTER_RESULT",
                        "day": str(day.date()),
                        "filter_code": code,
                        "hits": 0,
                        "duration_ms": dt,
                        "skipped": True,
                        "reason": reason,
                    }
                )
                continue
        unsafe_expr = bool(re.search(r"__|\bimport\b", expr))
        if unsafe_expr and not UNSAFE_EVAL:
            logger.warning(
                "Filter skipped due to unsafe expression",
                code=code,
                expr=expr,
                reason="UNSAFE_EXPR",
            )
            tokens = [tok for tok in _TOKEN_RE.findall(expr) if tok not in {"and", "or", "not"}]
            first_tok = tokens[0] if tokens else None
            for tok in tokens:
                if tok not in missing_cols_total:
                    logger.warning("missing_column:{}", tok)
                    missing_cols_total.add(tok)
            if first_tok is not None:
                logger.warning("skip filter: missing column {}", first_tok, code=code)
            skipped = True
            reason = "UNSAFE_EXPR"
            dt = int((time.perf_counter() - t0) * 1000)
            _log_event(
                {
                    "event": "FILTER_RESULT",
                    "day": str(day.date()),
                    "filter_code": code,
                    "hits": 0,
                    "duration_ms": dt,
                    "skipped": True,
                    "reason": reason,
                }
            )
            continue
        if unsafe_expr and UNSAFE_EVAL:
            logger.warning("Unsafe expression executed", code=code, expr=expr)

        filter_engine.UNSAFE_EVAL = UNSAFE_EVAL
        try:
            mask = _eval_expr(d, expr)
            mask = mask.reindex(d.index)
            filtered = d[mask]
        except (KeyError, NameError) as err:
            col = str(err).strip("'")
            if col not in missing_cols_total:
                logger.warning("missing_column:{}", col)
                missing_cols_total.add(col)
            logger.info("MISSING_COL_{}", col)
            logger.warning("skip filter: missing column {}", col, code=code)
            if stop_on_filter_error:
                raise ValueError(f"Filter {code!r} missing column {col}") from err
            skipped = True
            reason = f"MISSING_COL_{col}"
        except SyntaxError as err:
            if stop_on_filter_error:
                logger.error("Filter unsafe expression", code=code, expr=expr, reason=err)
                raise ValueError(f"Filter {code!r} unsafe expression: {err}") from err
            logger.warning(
                "Filter skipped due to unsafe expression",
                code=code,
                expr=expr,
                reason=err,
            )
            skipped = True
            reason = "SYNTAX_ERROR"
        except Exception as err:
            if raise_on_error:
                raise RuntimeError(f"Filter {code!r} failed: {err}") from err
            warnings.warn(f"Filter {code!r} failed: {err}")
            logger.warning("Filter {code!r} failed: {err}", code=code, err=err)
            skipped = True
            reason = str(err)
        else:
            if not filtered.empty:
                tmp = filtered.loc[:, ["symbol"]].copy()
                tmp["FilterCode"] = code
                if grp is not None:
                    tmp["Group"] = grp
                if side_norm is not None:
                    tmp["Side"] = side_norm
                tmp["Date"] = day
                out_frames.append(tmp)
                hits = len(tmp)
        dt = int((time.perf_counter() - t0) * 1000)
        _log_event(
            {
                "event": "FILTER_RESULT",
                "day": str(day.date()),
                "filter_code": code,
                "hits": hits,
                "duration_ms": dt,
                "skipped": skipped,
                "reason": reason,
            }
        )
    if missing_cols_total:
        logger.info("missing_column_total: {}", len(missing_cols_total))
    if not out_frames:
        logger.debug("run_screener end - no hits")
        return _empty_output()
    out = pd.concat(out_frames, ignore_index=True)
    out = out.rename(columns={"symbol": "Symbol"})
    out.drop_duplicates(["FilterCode", "Symbol", "Date"], inplace=True)
    cols = ["FilterCode"]
    if "Group" in out.columns:
        cols.append("Group")
    cols.append("Symbol")
    if "Side" in out.columns:
        cols.append("Side")
    cols.append("Date")
    out = out[cols]
    logger.debug("run_screener end - produced {rows_out} rows", rows_out=len(out))
    return out
