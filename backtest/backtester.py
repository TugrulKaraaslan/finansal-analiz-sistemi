from __future__ import annotations

import warnings
from enum import Enum

import numpy as np
import pandas as pd
from loguru import logger

from .calendars import (
    add_next_close,
    add_next_close_calendar,
    build_trading_days,
    check_missing_trading_days_by_symbol,
)


class TradeSide(Enum):
    LONG = "long"
    SHORT = "short"

    @classmethod
    def from_value(cls, value: str) -> "TradeSide":
        try:
            return cls(value.lower())
        except Exception as exc:
            # pragma: no cover - explicit ValueError below
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

    extras: list[pd.DataFrame] = []

    has_next = {"next_date", "next_close"}.issubset(df_with_next.columns)
    if not has_next:
        missing_days = check_missing_trading_days_by_symbol(df_with_next, raise_error=False)
        if missing_days:
            parts = []
            for sym, days in missing_days.items():
                day_str = ", ".join(d.strftime("%Y-%m-%d") for d in days)
                parts.append(f"{sym}: {day_str}")
            warnings.warn("Missing trading days: " + "; ".join(parts))
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
        invalid_side = pd.DataFrame()
        if invalid.any():
            bad_vals = sides[invalid].unique().tolist()
            logger.warning("dropping rows with invalid Side values: {bad}", bad=bad_vals)
            invalid_side = signals.loc[invalid].copy()
            invalid_side["Reason"] = "Invalid Side"
            invalid_side = invalid_side.assign(
                EntryClose=pd.NA,
                ExitClose=pd.NA,
                Side=pd.NA,
                ReturnPct=pd.NA,
                Win=pd.NA,
            )
            invalid_side["Date"] = pd.to_datetime(invalid_side["Date"]).dt.normalize()
            signals = signals.loc[valid_mask].copy()
            sides = sides.loc[valid_mask]
            if signals.empty:
                cols = [
                    "FilterCode",
                    "Symbol",
                    "Date",
                    "EntryClose",
                    "ExitClose",
                    "Side",
                    "ReturnPct",
                    "Win",
                    "Reason",
                ]
                if "Group" in invalid_side.columns:
                    cols.insert(1, "Group")
                extras.append(invalid_side[cols])
                return pd.concat(extras, ignore_index=True)
        signals = signals.copy()
        signals["Side"] = sides.replace("", "long").map(TradeSide.from_value)
    else:
        invalid_side = pd.DataFrame()

    if not invalid_side.empty:
        extras.append(invalid_side)

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
        merged.rename(columns={"next_date": "ExitDate", "next_close": "ExitClose"}, inplace=True)
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
                merged["ExitDate"] = pd.MultiIndex.from_frame(merged[["Symbol", "ExitDate"]]).map(
                    next_lookup
                )
            merged["ExitClose"] = pd.MultiIndex.from_frame(merged[["Symbol", "ExitDate"]]).map(
                close_lookup
            )

    invalid_entry = (merged["EntryClose"] <= 0) | merged["EntryClose"].isna()
    invalid_exit = (merged["ExitClose"] <= 0) | merged["ExitClose"].isna()
    invalid_prices = pd.DataFrame()
    if invalid_entry.any():
        logger.warning(
            "run_1g_returns dropping {n} rows with invalid EntryClose",
            n=int(invalid_entry.sum()),
        )
        invalid_prices = pd.concat(
            [
                invalid_prices,
                merged.loc[invalid_entry].assign(
                    Reason="Invalid EntryClose",
                    ReturnPct=pd.NA,
                    Win=pd.NA,
                ),
            ]
        )
    if invalid_exit.any():
        logger.warning(
            "run_1g_returns dropping {n} rows with invalid ExitClose",
            n=int(invalid_exit.sum()),
        )
        invalid_prices = pd.concat(
            [
                invalid_prices,
                merged.loc[invalid_exit & ~invalid_entry].assign(
                    Reason="Invalid ExitClose",
                    ReturnPct=pd.NA,
                    Win=pd.NA,
                ),
            ]
        )
    valid_mask_prices = ~(invalid_entry | invalid_exit)
    merged = merged.loc[valid_mask_prices].copy()

    if not invalid_prices.empty:
        extras.append(invalid_prices)

    merged["Reason"] = pd.NA
    if "Side" in merged.columns:
        side_enum = merged["Side"]
    else:
        side_enum = pd.Series(TradeSide.LONG, index=merged.index)
    pnl = merged["ExitClose"] / merged["EntryClose"] - 1.0
    sign = side_enum.map({TradeSide.SHORT: -1, TradeSide.LONG: 1})
    merged["Side"] = side_enum.map(lambda s: s.value)
    merged["ReturnPct"] = pnl * 100.0 * sign - float(transaction_cost)
    merged["Win"] = merged["ReturnPct"] > 0.0

    cols = ["FilterCode"]
    if "Group" in merged.columns or any("Group" in e.columns for e in extras):
        cols.append("Group")
    cols.extend(
        [
            "Symbol",
            "Date",
            "EntryClose",
            "ExitClose",
            "Side",
            "ReturnPct",
            "Win",
            "Reason",
        ]
    )
    out = merged[cols].copy()
    frames = [out]
    if extras:
        for ex in extras:
            for col in cols:
                if col not in ex.columns:
                    ex[col] = pd.NA
            ex = ex[cols]
            frames.append(ex)
    # Exclude empty or all-NA DataFrames to avoid pandas FutureWarning
    frames = [f.replace({pd.NA: np.nan}) for f in frames]
    frames = [f for f in frames if not f.dropna(how="all").empty]
    if not frames:
        out = pd.DataFrame(columns=cols)
    elif len(frames) == 1:
        out = frames[0]
    else:
        out = pd.concat(frames, ignore_index=True)
    logger.debug("run_1g_returns end - produced {rows_out} rows", rows_out=len(out))
    return out
