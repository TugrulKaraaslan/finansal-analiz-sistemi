# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from typing import Dict, List

import pandas as pd
import pandas_ta as ta


def compute_indicators(df: pd.DataFrame, params: Dict[str, List[int]]) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["symbol", "date"])
    out_frames = []
    for sym, g in df.groupby("symbol", group_keys=False):
        g = g.copy()
        for p in params.get("ema", [10, 20, 50]):
            col = f"EMA_{p}"
            g[col] = ta.ema(g["close"], length=int(p))
        for p in params.get("rsi", [14]):
            col = f"RSI_{p}"
            g[col] = ta.rsi(g["close"], length=int(p))
        macd_params = params.get("macd", [12, 26, 9])
        if len(macd_params) >= 3:
            fast, slow, sig = map(int, macd_params[:3])
            macd = ta.macd(g["close"], fast=fast, slow=slow, signal=sig)
            if macd is not None and not macd.empty:
                macd_cols = macd.columns.tolist()
                g[f"MACD_{fast}_{slow}_{sig}"] = macd[macd_cols[0]]
                g[f"MACD_{fast}_{slow}_{sig}_SIGNAL"] = macd[macd_cols[1]]
                g[f"MACD_{fast}_{slow}_{sig}_HIST"] = macd[macd_cols[2]]
        g["CHANGE_1D_PERCENT"] = g["close"].pct_change(1) * 100.0
        g["CHANGE_5D_PERCENT"] = g["close"].pct_change(5) * 100.0
        g["RELATIVE_VOLUME"] = g["volume"] / g["volume"].rolling(20).mean()
        out_frames.append(g)
    df2 = pd.concat(out_frames, ignore_index=True)
    for c in df2.columns:
        low = c.lower()
        if low not in df2.columns:
            df2[low] = df2[c]
    alias_map = {
        "rsi_14": "RSI_14",
        "ema_10": "EMA_10",
        "ema_20": "EMA_20",
        "ema_50": "EMA_50",
        "macd_12_26_9_hist": "MACD_12_26_9_HIST",
        "change_1d_percent": "CHANGE_1D_PERCENT",
        "change_1w_percent": "CHANGE_5D_PERCENT",
        "relative_volume": "RELATIVE_VOLUME",
    }
    alias_map_extra = {
        "degisim_1g_yuzde": "CHANGE_1D_PERCENT",
        "degisim_5g_yuzde": "CHANGE_5D_PERCENT",
        "hacim_goreli": "RELATIVE_VOLUME",
    }
    alias_map.update(alias_map_extra)
    for low, up in alias_map.items():
        if up in df2.columns:
            df2[low] = df2[up]
    return df2
