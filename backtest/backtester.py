# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from enum import Enum

import warnings
import pandas as pd
from loguru import logger

from .calendars import (
    add_next_close,
    add_next_close_calendar,
    build_trading_days,
    check_missing_trading_days,
)


class TradeSide(Enum):
    LONG = "long"
    SHORT = "short"

    @classmethod
    def from_value(cls, value: str) -> "TradeSide":
        try:
            return cls(value.lower())
        except Exception as exc:  # pragma: no cover - explicit ValueError below
            raise ValueError(f"Geçersiz Side değeri: {value!r}") from exc


def run_1g_returns(
    df_with_next: pd.DataFrame,
    signals: pd.DataFrame,
    holding_period: int = 1,
    transaction_cost: float = 0.0,
    trading_days: pd.DatetimeIndex | None = None,
) -> pd.DataFrame:
    """Calculate 1G returns for screener signals.

    Parameters
    ----------
    df_with_next : pandas.DataFrame
        Price data including ``symbol``, ``date`` and ``close`` columns. If
        ``next_close`` and ``next_date`` are missing they are computed
        automatically.
    signals : pandas.DataFrame
        Screener output containing at least ``FilterCode``, ``Symbol`` and
        ``Date`` columns.
    holding_period : int, default 1
        Number of trading days to hold each position.
    transaction_cost : float, default 0.0
        Commission or slippage in percentage points. Must be non-negative.
    trading_days : pandas.DatetimeIndex, optional
        Explicit trading calendar used to determine exit dates.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with calculated returns and win/loss flags for each signal.
    """

    logger.debug(
        "run_1g_returns start - base rows: {rows_base}, signals rows: {rows_sig}",
        rows_base=len(df_with_next) if isinstance(df_with_next, pd.DataFrame) else "?",
        rows_sig=len(signals) if isinstance(signals, pd.DataFrame) else "?",
    )

    if not isinstance(df_with_next, pd.DataFrame):
        logger.error("df_with_next must be a DataFrame")
        raise TypeError("df_with_next must be a DataFrame")
    if not isinstance(signals, pd.DataFrame):
        logger.error("signals must be a DataFrame")
        raise TypeError("signals must be a DataFrame")
    if not isinstance(holding_period, int) or holding_period < 1:
        raise ValueError("holding_period must be positive int")
    if not isinstance(transaction_cost, (int, float)):
        raise TypeError("transaction_cost must be numeric")
    if float(transaction_cost) < 0:
        raise ValueError("transaction_cost must be non-negative")

    if df_with_next.empty:
        logger.warning("df_with_next is empty")
        cols = [
            "FilterCode",
            "Symbol",
            "Date",
            "EntryClose",
            "ExitClose",
            "ReturnPct",
            "Win",
            "Reason",
        ]
        if "Group" in signals.columns:
            cols.insert(1, "Group")
        cols.insert(cols.index("ReturnPct"), "Side")
        empty_df = pd.DataFrame(columns=cols)
        empty_df["Side"] = pd.Series(dtype="object")
        return empty_df
    if signals.empty:
        logger.warning("signals DataFrame is empty")
        cols = [
            "FilterCode",
            "Symbol",
            "Date",
            "EntryClose",
            "ExitClose",
            "ReturnPct",
            "Win",
            "Reason",
        ]
        if "Group" in signals.columns:
            cols.insert(1, "Group")
        cols.insert(cols.index("ReturnPct"), "Side")
        empty_df = pd.DataFrame(columns=cols)
        empty_df["Side"] = pd.Series(dtype="object")
        return empty_df

    req_base = {"symbol", "date", "close"}
    missing_base = req_base.difference(df_with_next.columns)
    if missing_base:
        msg = f"Eksik kolon(lar): {', '.join(sorted(missing_base))}"
        logger.error(msg)
        raise ValueError(msg)

    req_sig = {"FilterCode", "Symbol", "Date"}
    missing_sig = req_sig.difference(signals.columns)
    if missing_sig:
        msg = f"Eksik kolon(lar): {', '.join(sorted(missing_sig))}"
        logger.error(msg)
        raise ValueError(msg)

    has_next = {"next_date", "next_close"}.issubset(df_with_next.columns)
    if not has_next:
        missing_days = check_missing_trading_days(df_with_next, raise_error=False)
        if not missing_days.empty:
            warnings.warn(
                "Missing trading days: "
                + ", ".join(d.strftime("%Y-%m-%d") for d in missing_days)
            )
        if trading_days is not None:
            df_with_next = add_next_close_calendar(df_with_next, trading_days)
        else:
            df_with_next = add_next_close(df_with_next)
        has_next = True

    if trading_days is None:
        trading_days = build_trading_days(df_with_next)

    if "Side" in signals.columns:
        sides = signals["Side"].fillna("").astype(str).str.lower()
        valid_mask = sides.isin([s.value for s in TradeSide]) | (sides == "")
        invalid = ~valid_mask
        if invalid.any():
            bad_vals = sides[invalid].unique().tolist()
            logger.warning(
                "dropping rows with invalid Side values: {bad}", bad=bad_vals
            )
            signals = signals.loc[valid_mask].copy()
            sides = sides.loc[valid_mask]
            if signals.empty:
                logger.warning("signals DataFrame is empty after dropping invalid Side")
                cols = [
                    "FilterCode",
                    "Symbol",
                    "Date",
                    "EntryClose",
                    "ExitClose",
                    "ReturnPct",
                    "Win",
                    "Reason",
                ]
                if "Group" in signals.columns:
                    cols.insert(1, "Group")
                cols.insert(cols.index("ReturnPct"), "Side")
                empty_df = pd.DataFrame(columns=cols)
                empty_df["Side"] = pd.Series(dtype="object")
                return empty_df
        signals = signals.copy()
        signals["Side"] = sides.replace("", "long").map(TradeSide.from_value)

    has_next = {"next_date", "next_close"}.issubset(df_with_next.columns)
    base_cols = ["symbol", "date", "close"]
    if has_next:
        base_cols.extend(["next_date", "next_close"])
    base = df_with_next[base_cols].copy()
    base["date"] = pd.to_datetime(base["date"]).dt.normalize()
    if has_next:
        base["next_date"] = pd.to_datetime(base["next_date"]).dt.normalize()
    before = len(base)
    base = base.drop_duplicates(["symbol", "date"])
    if len(base) != before:
        logger.warning("dropped {n} duplicate price rows", n=before - len(base))

    signals = signals.copy()
    signals["Date"] = pd.to_datetime(signals["Date"]).dt.normalize()
    before_sig = len(signals)
    signals = signals.drop_duplicates()
    if len(signals) != before_sig:
        logger.warning("dropped {n} duplicate signal rows", n=before_sig - len(signals))
    if trading_days is not None and not isinstance(trading_days, pd.DatetimeIndex):
        raise TypeError("trading_days must be a DatetimeIndex")

    merged = signals.merge(
        base, left_on=["Symbol", "Date"], right_on=["symbol", "date"], how="left"
    )
    merged.rename(columns={"close": "EntryClose"}, inplace=True)
    merged = merged.drop(columns=["symbol", "date"])

    if has_next and holding_period == 1:
        merged.rename(
            columns={"next_date": "ExitDate", "next_close": "ExitClose"}, inplace=True
        )
    else:
        if trading_days is not None:
            td = pd.DatetimeIndex(trading_days).normalize()
            td_pos = pd.Series(range(len(td)), index=td)

            def calc_exit(d: pd.Timestamp) -> pd.Timestamp:
                idx = td_pos.get(d, None)
                if idx is None or idx + holding_period >= len(td):
                    return pd.NaT
                return td[idx + holding_period]

            merged["ExitDate"] = merged["Date"].map(calc_exit)
            exit_base = base.drop(columns=["next_date", "next_close"], errors="ignore").rename(
                columns={"symbol": "Symbol", "date": "ExitDate", "close": "ExitClose"}
            )
            merged = merged.merge(exit_base, on=["Symbol", "ExitDate"], how="left")
        else:
            next_lookup = base.set_index(["symbol", "date"])["next_date"]
            close_lookup = base.set_index(["symbol", "date"])["close"]
            merged["ExitDate"] = merged["Date"]
            for _ in range(holding_period):
                merged["ExitDate"] = (
                    pd.MultiIndex.from_frame(merged[["Symbol", "ExitDate"]])
                    .map(next_lookup)
                )
            merged["ExitClose"] = (
                pd.MultiIndex.from_frame(merged[["Symbol", "ExitDate"]])
                .map(close_lookup)
            )

    invalid_entry = (merged["EntryClose"] <= 0) | merged["EntryClose"].isna()
    invalid_exit = (merged["ExitClose"] <= 0) | merged["ExitClose"].isna()
    merged["Reason"] = pd.NA
    if invalid_entry.any():
        logger.warning(
            "run_1g_returns marking {n} rows with invalid EntryClose",
            n=int(invalid_entry.sum()),
        )
        merged.loc[invalid_entry, "Reason"] = "invalid_entry"
    if invalid_exit.any():
        logger.warning(
            "run_1g_returns marking {n} rows with invalid ExitClose",
            n=int(invalid_exit.sum()),
        )
        merged.loc[invalid_exit & merged["Reason"].isna(), "Reason"] = "invalid_exit"

    valid = ~(invalid_entry | invalid_exit)
    if "Side" in merged.columns:
        side_enum = merged.loc[valid, "Side"]
    else:
        side_enum = pd.Series(TradeSide.LONG, index=merged.index)
        side_enum = side_enum.loc[valid]
    pnl = merged.loc[valid, "ExitClose"] / merged.loc[valid, "EntryClose"] - 1.0
    sign = side_enum.map({TradeSide.SHORT: -1, TradeSide.LONG: 1})
    merged.loc[valid, "Side"] = side_enum.map(lambda s: s.value)
    merged.loc[valid, "ReturnPct"] = pnl * 100.0 * sign - float(transaction_cost)
    merged.loc[valid, "Win"] = merged.loc[valid, "ReturnPct"] > 0.0

    cols = ["FilterCode"]
    if "Group" in merged.columns:
        cols.append("Group")
    cols.extend(["Symbol", "Date", "EntryClose", "ExitClose"])
    if "Side" in merged.columns:
        cols.append("Side")
    cols.extend(["ReturnPct", "Win"])
    if "Reason" in merged.columns:
        cols.append("Reason")
    out = merged[cols].copy()
    logger.debug("run_1g_returns end - produced {rows_out} rows", rows_out=len(out))
    return out
