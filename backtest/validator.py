# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import pandas as pd


def dataset_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return simple stats per symbol: first/last date, rows, NA close
    count, dup count."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"Eksik kolon(lar): {', '.join(sorted(missing))}")  # TİP DÜZELTİLDİ
    if df.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "rows",
                "first_date",
                "last_date",
                "na_close",
                "dup_symbol_date",
            ]
        )
    dup = df.duplicated(["symbol", "date"]).groupby(df["symbol"]).sum()
    na_close = df["close"].isna().groupby(df["symbol"]).sum()
    grp = df.groupby("symbol")
    out = grp.agg(
        rows=("date", "size"), first_date=("date", "min"), last_date=("date", "max")
    ).reset_index()
    out["na_close"] = out["symbol"].map(na_close).fillna(0).astype(int)
    out["dup_symbol_date"] = out["symbol"].map(dup).fillna(0).astype(int)
    return out.sort_values("symbol").reset_index(drop=True)


def quality_warnings(df: pd.DataFrame) -> pd.DataFrame:
    """Return row-level issues for quick inspection (date order, negative
    prices, etc.)."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"Eksik kolon(lar): {', '.join(sorted(missing))}")  # TİP DÜZELTİLDİ
    issues = []
    if df.empty:
        return pd.DataFrame(columns=["symbol", "date", "issue", "value"])
    g = df.sort_values(["symbol", "date"]).groupby("symbol")
    for sym, x in g:
        # non-monotonic date
        if not x["date"].is_monotonic_increasing:
            issues.append(
                {
                    "symbol": sym,
                    "date": None,
                    "issue": "non_monotonic_dates",
                    "value": "",
                }
            )
        # negative/zero close
        bad = x[x["close"] <= 0]
        for _, r in bad.iterrows():
            issues.append(
                {
                    "symbol": sym,
                    "date": r["date"],
                    "issue": "non_positive_close",
                    "value": r["close"],
                }
            )
    return pd.DataFrame(issues)
