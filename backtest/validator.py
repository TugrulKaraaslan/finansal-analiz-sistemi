from __future__ import annotations

import pandas as pd


def dataset_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return simple stats per symbol: first/last date, rows, NA close
    count, dup count."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"Eksik kolon(lar): {', '.join(sorted(missing))}")
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
        raise TypeError("df must be a DataFrame")
    req = {"symbol", "date", "close"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"Eksik kolon(lar): {', '.join(sorted(missing))}")
    issues = []
    if df.empty:
        return pd.DataFrame(columns=["symbol", "date", "issue", "value"])
    g = df.sort_values(["symbol", "date"]).groupby("symbol")
    for sym, x in g:
        if not x["date"].is_monotonic_increasing:
            issues.append(
                {
                    "symbol": sym,
                    "date": None,
                    "issue": "non_monotonic_dates",
                    "value": "",
                }
            )
        bad_close = x[x["close"] <= 0]
        for _, r in bad_close.iterrows():
            issues.append(
                {
                    "symbol": sym,
                    "date": r["date"],
                    "issue": "non_positive_close",
                    "value": r["close"],
                }
            )
        if "volume" in x.columns:
            bad_vol = x[x["volume"] <= 0]
            for _, r in bad_vol.iterrows():
                issues.append(
                    {
                        "symbol": sym,
                        "date": r["date"],
                        "issue": "non_positive_volume",
                        "value": r["volume"],
                    }
                )
        if {"high", "low"}.issubset(x.columns):
            bad_hl = x[x["high"] < x["low"]]
            for _, r in bad_hl.iterrows():
                issues.append(
                    {
                        "symbol": sym,
                        "date": r["date"],
                        "issue": "high_lt_low",
                        "value": f"{r['high']}<{r['low']}",
                    }
                )
        if "open" in x.columns:
            na_open = x[x["open"].isna()]
            for _, r in na_open.iterrows():
                issues.append(
                    {
                        "symbol": sym,
                        "date": r["date"],
                        "issue": "na_open",
                        "value": "",
                    }
                )
        na_close = x[x["close"].isna()]
        for _, r in na_close.iterrows():
            issues.append(
                {
                    "symbol": sym,
                    "date": r["date"],
                    "issue": "na_close",
                    "value": "",
                }
            )
    if not issues:
        return pd.DataFrame(columns=["symbol", "date", "issue", "value"])
    return pd.DataFrame(issues, columns=["symbol", "date", "issue", "value"])
