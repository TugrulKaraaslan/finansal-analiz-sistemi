from __future__ import annotations

import re
import re
import warnings

import pandas as pd
from loguru import logger

from backtest.columns import canonical_map
from .expr import evaluate


def _to_pandas_ops(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


def _eval_expr(df: pd.DataFrame, expr: str) -> pd.Series:
    return evaluate(df, expr)


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
    for code, expr, grp, side in zip(
        filters_df["FilterCode"], filters_df["expr"], groups, sides
    ):
        side_norm = None
        if pd.notna(side) and str(side).strip():
            side_norm = str(side).strip().lower()
            if side_norm not in {"long", "short"}:
                msg = f"Filter {code!r} has invalid Side {side!r}"
                if stop_on_filter_error:
                    logger.error("Filter invalid Side", code=code, side=side)
                    raise ValueError(msg)
                logger.warning(
                    "Filter skipped due to invalid Side", code=code, side=side
                )
                continue
        try:
            mask = _eval_expr(d, expr)
            mask = mask.reindex(d.index)
            filtered = d[mask]
        except (KeyError, NameError) as err:
            col = str(err).strip("'")
            if col not in missing_cols_total:
                logger.warning("missing_column:{}", col)
                missing_cols_total.add(col)
            logger.warning("skip filter: missing column {}", col, code=code)
            if stop_on_filter_error:
                raise ValueError(f"Filter {code!r} missing column {col}") from err
            continue
        except SyntaxError as err:
            if stop_on_filter_error:
                logger.error(
                    "Filter unsafe expression", code=code, expr=expr, reason=err
                )
                raise ValueError(f"Filter {code!r} unsafe expression: {err}") from err
            logger.warning(
                "Filter skipped due to unsafe expression",
                code=code,
                expr=expr,
                reason=err,
            )
            continue
        except Exception as err:
            if raise_on_error:
                raise RuntimeError(f"Filter {code!r} failed: {err}") from err
            warnings.warn(f"Filter {code!r} failed: {err}")
            logger.warning("Filter {code!r} failed: {err}", code=code, err=err)
            continue
        if filtered.empty:
            continue
        tmp = filtered.loc[:, ["symbol"]].copy()
        tmp["FilterCode"] = code
        if grp is not None:
            tmp["Group"] = grp
        if side_norm is not None:
            tmp["Side"] = side_norm
        tmp["Date"] = day
        out_frames.append(tmp)
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
