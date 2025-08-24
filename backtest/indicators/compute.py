from __future__ import annotations

import pandas as pd


def ensure_stochrsi(df: pd.DataFrame, rsi_len: int, k: int, d: int, smooth: int) -> pd.DataFrame:
    """Ensure StochRSI %K and %D columns exist on ``df``.

    The resulting column names follow the pattern
    ``stochrsi_k_{rsi_len}_{k}_{d}_{smooth}`` and ``stochrsi_d_{rsi_len}_{k}_{d}_{smooth}``.
    """

    k_col = f"stochrsi_k_{rsi_len}_{k}_{d}_{smooth}"
    d_col = f"stochrsi_d_{rsi_len}_{k}_{d}_{smooth}"
    if k_col in df.columns and d_col in df.columns:
        return df

    close = df["close"]
    rsi = close.diff().pipe(
        lambda s: s.clip(lower=0).ewm(alpha=1 / rsi_len).mean()
        / (-s.clip(upper=0).ewm(alpha=1 / rsi_len).mean())
    )
    rsi = 100 - (100 / (1 + rsi))
    min_rsi = rsi.rolling(k).min()
    max_rsi = rsi.rolling(k).max()
    stoch = (rsi - min_rsi) / (max_rsi - min_rsi)
    stoch_k = stoch.rolling(smooth).mean()
    stoch_d = stoch_k.rolling(d).mean()
    df[k_col] = stoch_k
    df[d_col] = stoch_d
    return df


def ensure_mom(df: pd.DataFrame, n: int) -> pd.DataFrame:
    col = f"mom_{n}"
    if col not in df.columns:
        df[col] = df["close"].diff(n)
    return df


def ensure_roc(df: pd.DataFrame, n: int) -> pd.DataFrame:
    col = f"roc_{n}"
    if col not in df.columns:
        df[col] = df["close"].pct_change(n)
    return df


def ensure_cci(df: pd.DataFrame, n: int) -> pd.DataFrame:
    col = f"cci_{n}"
    if col in df.columns:
        return df
    tp = (df["high"] + df["low"] + df["close"]) / 3
    sma = tp.rolling(n).mean()
    md = (tp - sma).abs().rolling(n).mean()
    df[col] = (tp - sma) / (0.015 * md)
    return df


__all__ = ["ensure_stochrsi", "ensure_mom", "ensure_roc", "ensure_cci"]
