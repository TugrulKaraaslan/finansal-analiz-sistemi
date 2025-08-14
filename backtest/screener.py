from __future__ import annotations

import re
import warnings
import operator

import numpy as np
import pandas as pd
from loguru import logger

from backtest.query_parser import SafeQuery


def _to_series(x):
    import pandas as pd

    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 1:
            return x.iloc[:, 0]
        return x.any(axis=1)
    return x


def _align_series(a, b):
    if not hasattr(a, "index") or not hasattr(b, "index"):
        return a, b
    idx = a.index.intersection(b.index)
    return a.reindex(idx), b.reindex(idx)


def _to_pandas_ops(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


class _SeriesWrapper:
    __array_priority__ = 1000

    def __init__(self, data):
        self.data = _to_series(data)

    # --- comparison and boolean ops ---
    def _binary(self, other, op):
        other_val = getattr(other, "data", other)
        other_val = _to_series(other_val)
        a, b = _align_series(self.data, other_val)
        res = op(a, b)
        return _SeriesWrapper(res)

    def __and__(self, other):
        return self._binary(other, operator.and_)

    def __rand__(self, other):
        return self.__and__(other)

    def __or__(self, other):
        return self._binary(other, operator.or_)

    def __ror__(self, other):
        return self.__or__(other)

    def __gt__(self, other):
        return self._binary(other, operator.gt)

    def __ge__(self, other):
        return self._binary(other, operator.ge)

    def __lt__(self, other):
        return self._binary(other, operator.lt)

    def __le__(self, other):
        return self._binary(other, operator.le)

    def __eq__(self, other):  # noqa: D401
        return self._binary(other, operator.eq)

    def __ne__(self, other):  # noqa: D401
        return self._binary(other, operator.ne)

    # --- arithmetic ops ---
    def __add__(self, other):
        return self._binary(other, operator.add)

    def __radd__(self, other):
        return _SeriesWrapper(other).__add__(self)

    def __sub__(self, other):
        return self._binary(other, operator.sub)

    def __rsub__(self, other):
        return _SeriesWrapper(other).__sub__(self)

    def __mul__(self, other):
        return self._binary(other, operator.mul)

    def __rmul__(self, other):
        return _SeriesWrapper(other).__mul__(self)

    def __truediv__(self, other):
        return self._binary(other, operator.truediv)

    def __rtruediv__(self, other):
        return _SeriesWrapper(other).__truediv__(self)

    def __floordiv__(self, other):
        return self._binary(other, operator.floordiv)

    def __rfloordiv__(self, other):
        return _SeriesWrapper(other).__floordiv__(self)

    def __pow__(self, other):
        return self._binary(other, operator.pow)

    def __rpow__(self, other):
        return _SeriesWrapper(other).__pow__(self)

    def __neg__(self):
        return _SeriesWrapper(-self.data)

    def __pos__(self):
        return self

    def __invert__(self):
        return _SeriesWrapper(~_to_series(self.data))

    def __abs__(self):
        return _SeriesWrapper(abs(self.data))

    # --- attribute access ---
    def __getattr__(self, name):
        attr = getattr(self.data, name)
        if callable(attr):

            def wrapped(*args, **kwargs):
                args = [getattr(a, "data", a) for a in args]
                kwargs = {k: getattr(v, "data", v) for k, v in kwargs.items()}
                res = attr(*args, **kwargs)
                return _SeriesWrapper(res)

            return wrapped
        return _SeriesWrapper(attr)

    def unwrap(self):
        return _to_series(self.data)


def _wrap_func(func):
    def inner(*args, **kwargs):
        args = [getattr(a, "data", a) for a in args]
        kwargs = {k: getattr(v, "data", v) for k, v in kwargs.items()}
        res = func(*args, **kwargs)
        return _SeriesWrapper(res)

    return inner


def _eval_expr(df: pd.DataFrame, expr: str) -> pd.Series:
    env = {name: _SeriesWrapper(df[name]) for name in df.columns}
    env.update(
        {
            "abs": _wrap_func(abs),
            "max": _wrap_func(np.maximum),
            "min": _wrap_func(np.minimum),
            "log": _wrap_func(np.log),
            "exp": _wrap_func(np.exp),
            "floor": _wrap_func(np.floor),
            "ceil": _wrap_func(np.ceil),
        }
    )
    result = eval(expr, {"__builtins__": {}}, env)
    if isinstance(result, _SeriesWrapper):
        result = result.unwrap()
    result = _to_series(result)
    if not pd.api.types.is_bool_dtype(result):
        raise ValueError("Query expression must evaluate to a boolean mask")
    return result


def run_screener(
    df_ind: pd.DataFrame,
    filters_df: pd.DataFrame,
    date,
    stop_on_filter_error: bool = False,
    raise_on_error: bool = True,
) -> pd.DataFrame:
    """Run the screener filters for a given date.

    Parameters
    ----------
    df_ind : pd.DataFrame
        Indicator data with at least ``symbol`` and ``date`` columns.
    filters_df : pd.DataFrame
        DataFrame describing the filter expressions.
    date : datetime-like
        The date to evaluate the filters on.
    stop_on_filter_error : bool, optional
        If ``True``, any filter referencing missing columns raises a
        :class:`ValueError`. When ``False`` (default) such filters are skipped
        with a warning.
    raise_on_error : bool, optional
        Controls behaviour when a filter's expression fails to evaluate.
        When ``True`` (default) a :class:`RuntimeError` is raised
        immediately.  When ``False`` the error is logged and a warning is
        emitted, allowing processing to continue.

    Returns
    -------
    pd.DataFrame
        Resulting matches for each filter.
    """
    logger.debug(
        "run_screener start - data rows: {rows_df}, "
        "filter rows: {rows_filters}, date: {day}",
        rows_df=len(df_ind) if isinstance(df_ind, pd.DataFrame) else "?",
        rows_filters=len(filters_df) if isinstance(filters_df, pd.DataFrame) else "?",
        day=date,
    )

    if not isinstance(df_ind, pd.DataFrame):
        logger.error("df_ind must be a DataFrame")
        raise TypeError("df_ind must be a DataFrame")
    if not isinstance(filters_df, pd.DataFrame):
        logger.error("filters_df must be a DataFrame")
        raise TypeError("filters_df must be a DataFrame")

    if df_ind.empty:
        logger.error("df_ind is empty")
        raise ValueError("df_ind is empty")
    if filters_df.empty:
        logger.error("filters_df is empty")
        raise ValueError("filters_df is empty")

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

    df_ind = df_ind.copy()
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
    valids = []
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
        sq = SafeQuery(expr)
        if not sq.is_safe:
            msg = f"Filter {code!r} unsafe expression: {sq.error}"
            if stop_on_filter_error:
                logger.error(
                    "Filter unsafe expression", code=code, expr=expr, reason=sq.error
                )
                raise ValueError(msg)
            logger.warning(
                "Filter skipped due to unsafe expression",
                code=code,
                expr=expr,
                reason=sq.error,
            )
            continue
        missing_cols = sq.names.difference(d.columns)
        if missing_cols:
            msg = f"Filter {code!r} missing columns: {sorted(missing_cols)}"
            if stop_on_filter_error:
                logger.error(
                    "Filter missing columns",
                    code=code,
                    missing=sorted(missing_cols),
                )
                raise ValueError(msg)
            missing = ", ".join(sorted(missing_cols))
            logger.warning("skip filter: missing column {}", missing, code=code)
            continue
        valids.append((code, grp, side_norm, sq))
    out_frames = []
    for code, grp, side_norm, sq in valids:
        try:
            mask = _eval_expr(d, sq.expr)
            mask = _to_series(mask)
            mask = mask.reindex(d.index)
            filtered = d[mask]
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
