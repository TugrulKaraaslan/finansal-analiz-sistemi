# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from typing import Iterable, Optional, Set

import pandas as pd


def add_next_close(df: pd.DataFrame) -> pd.DataFrame:
    """Price-driven next bar (symbol-based)."""
    df = df.copy().sort_values(["symbol", "date"])
    df["next_date"] = df.groupby("symbol")["date"].shift(-1)
    df["next_close"] = df.groupby("symbol")["close"].shift(-1)
    return df


def load_holidays_csv(path: str) -> Set[pd.Timestamp]:
    """Read holiday CSV with a 'date' column (case-insens.),
    return set of Timestamps (date only)."""
    h = pd.read_csv(path)
    cols = {c.lower(): c for c in h.columns}
    c_date = cols.get("date") or list(h.columns)[0]
    h[c_date] = pd.to_datetime(h[c_date]).dt.normalize()
    return set(h[c_date].unique())


def is_weekend(ts: pd.Timestamp) -> bool:
    return ts.weekday() >= 5  # 5=Sat,6=Sun


def build_trading_days(
    df: pd.DataFrame, holidays: Optional[Iterable[pd.Timestamp]] = None
) -> pd.DatetimeIndex:
    """Build calendar trading days from min..max of df, excluding weekends
    and holidays."""
    if df.empty:
        return pd.DatetimeIndex([])
    start = pd.to_datetime(df["date"]).min()
    end = pd.to_datetime(df["date"]).max()
    all_days = pd.date_range(start=start, end=end, freq="D")
    hol = set(pd.to_datetime(list(holidays))) if holidays is not None else set()
    trade = [d for d in all_days if (not is_weekend(d)) and (d.normalize() not in hol)]
    return pd.DatetimeIndex(trade)


def add_next_close_calendar(
    df: pd.DataFrame, trading_days: pd.DatetimeIndex
) -> pd.DataFrame:
    """Calendar-driven next business day: next_date = next trading day (global).
    next_close is taken from symbol's close at that date; if missing,
    remains NaN (no trade possible).
    """
    df = df.copy().sort_values(["symbol", "date"])
    # map current date -> next trading day
    td = pd.Series(trading_days[1:].values, index=trading_days[:-1]).to_dict()
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
