# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Set

import pandas as pd

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
        if isinstance(holidays, Iterable) and not isinstance(holidays, (str, bytes, pd.Timestamp)):
            hol_iter = list(holidays)
        else:
            hol_iter = [holidays]
        try:
            hol = set(pd.to_datetime(hol_iter).normalize())  # TİP DÜZELTİLDİ
        except Exception as e:  # pragma: no cover - defensive
            raise ValueError("holidays contains non-date values") from e  # TİP DÜZELTİLDİ
    else:
        hol = set()
    trade = [d for d in all_days if (not is_weekend(d)) and (d.normalize() not in hol)]
    return pd.DatetimeIndex(trade)


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
    # map current date -> next trading day
    td = dict(zip(trading_days[:-1], trading_days[1:]))  # TİP DÜZELTİLDİ
    dates = pd.to_datetime(df["date"])
    next_dates = dates.apply(lambda d: td.get(pd.Timestamp(d).normalize(), pd.NaT))
    df["next_date"] = next_dates.dt.date
    # merge to get next_close for same symbol & next_date
    base = df[["symbol", "date", "close"]].copy()
    base.columns = ["symbol", "date", "close_curr"]
    # align df next_date with base date to pick next_close
    m = df.merge(
        base.rename(columns={"date": "next_date", "close_curr": "next_close"}),
        on=["symbol", "next_date"],
        how="left",
    )
    df["next_close"] = m["next_close"].values
    return df
