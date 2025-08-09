# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Set

import pandas as pd
import warnings

from utils.paths import resolve_path


def add_next_close(df: pd.DataFrame) -> pd.DataFrame:
    """Price-driven next bar (symbol-based)."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(
            f"Eksik kolon(lar): {', '.join(sorted(missing))}"
        )  # TİP DÜZELTİLDİ
    df = df.copy().sort_values(["symbol", "date"])
    df["next_date"] = df.groupby("symbol")["date"].shift(-1)
    df["next_close"] = df.groupby("symbol")["close"].shift(-1)
    return df


def load_holidays_csv(path: str | Path) -> Set[pd.Timestamp]:
    """Read holiday CSV with a 'date' column (case-insens.),
    return set of Timestamps (date only)."""
    if not isinstance(path, (str, bytes, Path)):
        raise TypeError("path must be a string or Path")
    p = resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"Tatil CSV bulunamadı: {p}")
    try:
        h = pd.read_csv(p, encoding="utf-8")
    except Exception as e:
        raise FileNotFoundError(f"Tatil CSV okunamadı: {p}") from e
    if h.empty:
        return set()
    cols = {c.lower(): c for c in h.columns}
    c_date = cols.get("date")
    if c_date is None:
        raise ValueError("CSV must contain a 'date' column")  # TİP DÜZELTİLDİ
    h[c_date] = pd.to_datetime(h[c_date]).dt.normalize()
    return set(h[c_date].unique())


def is_weekend(ts: pd.Timestamp) -> bool:
    return ts.weekday() >= 5  # 5=Sat,6=Sun


def build_trading_days(
    df: pd.DataFrame, holidays: Optional[Iterable[pd.Timestamp]] = None
) -> pd.DatetimeIndex:
    """Build calendar trading days from min..max of df, excluding weekends
    and holidays."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    if df.empty:
        return pd.DatetimeIndex([])
    start = pd.to_datetime(df["date"]).min()
    end = pd.to_datetime(df["date"]).max()
    all_days = pd.date_range(start=start, end=end, freq="D")
    if holidays is not None:
        if isinstance(holidays, (int, float)):
            raise TypeError("holidays must be iterable or date-like")  # TİP DÜZELTİLDİ
        if isinstance(holidays, Iterable) and not isinstance(
            holidays, (str, bytes, pd.Timestamp)
        ):
            hol_iter = list(holidays)
        else:
            hol_iter = [holidays]
        try:
            hol = set(pd.to_datetime(hol_iter).normalize())  # TİP DÜZELTİLDİ
        except Exception as e:  # pragma: no cover - defensive
            raise ValueError(
                "holidays contains non-date values"
            ) from e  # TİP DÜZELTİLDİ
    else:
        hol = set()
    trade = [d for d in all_days if (not is_weekend(d)) and (d.normalize() not in hol)]
    return pd.DatetimeIndex(trade)


def check_missing_trading_days(
    df: pd.DataFrame,
    holidays: Optional[Iterable[pd.Timestamp]] = None,
    *,
    raise_error: bool = True,
) -> pd.DatetimeIndex:
    """Compare actual data dates with expected trading days.

    If any trading days are missing from the DataFrame, either raise ``ValueError``
    or emit a ``UserWarning`` depending on ``raise_error``. Returns the missing
    days as a ``DatetimeIndex``.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")

    trading_days = build_trading_days(df, holidays)
    actual = set(pd.to_datetime(df["date"]).dt.normalize())
    missing = pd.DatetimeIndex([d for d in trading_days if d not in actual])

    if len(missing) > 0:
        msg = "Missing trading days: " + ", ".join(d.strftime("%Y-%m-%d") for d in missing)
        if raise_error:
            raise ValueError(msg)
        else:  # pragma: no cover - warning path
            warnings.warn(msg)
    return missing


def check_missing_trading_days_by_symbol(
    df: pd.DataFrame,
    holidays: Optional[Iterable[pd.Timestamp]] = None,
    *,
    raise_error: bool = True,
) -> dict[str, pd.DatetimeIndex]:
    """Check missing trading days separately for each symbol.

    Returns a mapping from symbol to a ``DatetimeIndex`` of missing days.
    If any symbol has missing days, either raises ``ValueError`` or emits a
    warning depending on ``raise_error``.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")

    missing: dict[str, pd.DatetimeIndex] = {}
    for sym, sub in df.groupby("symbol"):
        miss = check_missing_trading_days(sub, holidays, raise_error=False)
        if len(miss) > 0:
            missing[sym] = miss

    if missing:
        parts = []
        for sym, days in missing.items():
            day_str = ", ".join(d.strftime("%Y-%m-%d") for d in days)
            parts.append(f"{sym}: {day_str}")
        msg = "Missing trading days: " + "; ".join(parts)
        if raise_error:
            raise ValueError(msg)
        else:  # pragma: no cover - warning path
            warnings.warn(msg)
    return missing


def add_next_close_calendar(
    df: pd.DataFrame, trading_days: pd.DatetimeIndex
) -> pd.DataFrame:
    """Calendar-driven next business day: next_date = next trading day (global).
    next_close is taken from symbol's close at that date; if missing,
    remains NaN (no trade possible).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(
            f"Eksik kolon(lar): {', '.join(sorted(missing))}"
        )  # TİP DÜZELTİLDİ
    if not isinstance(trading_days, pd.DatetimeIndex):
        raise TypeError("trading_days must be a DatetimeIndex")  # TİP DÜZELTİLDİ
    df = df.copy().sort_values(["symbol", "date"])
    dates = pd.to_datetime(df["date"]).dt.normalize()
    pos = trading_days.get_indexer(dates)
    valid_pos = pos >= 0
    next_pos = pos.copy()
    next_pos[valid_pos] = pos[valid_pos] + 1
    next_dates = pd.Series(pd.NaT, dtype="datetime64[ns]", index=df.index)
    mask = valid_pos & (next_pos < len(trading_days))
    next_dates.loc[mask] = trading_days[next_pos[mask]]
    df["next_date"] = next_dates
    base = df[["symbol", "date", "close"]].copy()
    base.columns = ["symbol", "date", "close_curr"]
    m = df.merge(
        base.rename(columns={"date": "next_date", "close_curr": "next_close"}),
        on=["symbol", "next_date"],
        how="left",
    )
    df["next_close"] = m["next_close"].values
    return df
