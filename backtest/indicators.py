# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
from loguru import logger


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _rsi(series: pd.Series, length: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1 / length, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_indicators(
    df: pd.DataFrame,
    params: Optional[Dict[str, List[int]]] = None,
    *,
    engine: str = "builtin",
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    if params is not None and not isinstance(params, dict):
        raise TypeError("params must be a dict or None")  # TİP DÜZELTİLDİ
    if params is None:
        params = {}  # TİP DÜZELTİLDİ
    if df.empty:
        return df.copy()  # TİP DÜZELTİLDİ
    req = {"symbol", "date", "close", "volume"}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"Eksik kolon(lar): {', '.join(sorted(missing))}")
    df = df.copy()
    df = df.sort_values(["symbol", "date"])

    use_pandas_ta = engine == "pandas_ta"
    ta = None
    if use_pandas_ta:
        try:  # pragma: no cover - optional dependency
            import pandas_ta as ta  # noqa: WPS433
        except ModuleNotFoundError:  # pragma: no cover
            logger.warning(
                "pandas_ta kütüphanesi bulunamadı, builtin hesaplamalara dönülüyor",
            )
            use_pandas_ta = False
    out_frames = []
    for sym, g in df.groupby("symbol", group_keys=False):
        g = g.copy()
        ema_params = params.get("ema", [10, 20, 50])
        if isinstance(ema_params, (int, float)):
            ema_params = [ema_params]  # TİP DÜZELTİLDİ
        for p in ema_params:
            col = f"EMA_{p}"
            if use_pandas_ta and ta is not None:
                g[col] = ta.ema(g["close"], length=int(p))
            else:
                g[col] = _ema(g["close"], int(p))
        rsi_params = params.get("rsi", [14])
        if isinstance(rsi_params, (int, float)):
            rsi_params = [rsi_params]  # TİP DÜZELTİLDİ
        for p in rsi_params:
            col = f"RSI_{p}"
            if use_pandas_ta and ta is not None:
                g[col] = ta.rsi(g["close"], length=int(p))
            else:
                g[col] = _rsi(g["close"], int(p))
        macd_params = params.get("macd", [])
        if macd_params:
            if isinstance(macd_params, (int, float)):
                macd_params = [macd_params]  # TİP DÜZELTİLDİ
            macd_params = list(macd_params)
            if len(macd_params) < 3:
                raise ValueError(
                    "macd params must have at least three values",
                )  # TİP DÜZELTİLDİ
            fast, slow, sig = map(int, macd_params[:3])
            if use_pandas_ta and ta is not None:
                macd = ta.macd(g["close"], fast=fast, slow=slow, signal=sig)
                if macd is not None and not macd.empty:
                    macd_cols = macd.columns.tolist()
                    g[f"MACD_{fast}_{slow}_{sig}"] = macd[macd_cols[0]]
                    g[f"MACD_{fast}_{slow}_{sig}_SIGNAL"] = macd[macd_cols[1]]
                    g[f"MACD_{fast}_{slow}_{sig}_HIST"] = macd[macd_cols[2]]
            else:
                ema_fast = _ema(g["close"], fast)
                ema_slow = _ema(g["close"], slow)
                macd_line = ema_fast - ema_slow
                signal_line = _ema(macd_line, sig)
                hist = macd_line - signal_line
                g[f"MACD_{fast}_{slow}_{sig}"] = macd_line
                g[f"MACD_{fast}_{slow}_{sig}_SIGNAL"] = signal_line
                g[f"MACD_{fast}_{slow}_{sig}_HIST"] = hist
        g["CHANGE_1D_PERCENT"] = g["close"].pct_change(1) * 100.0
        g["CHANGE_5D_PERCENT"] = g["close"].pct_change(5) * 100.0
        g["RELATIVE_VOLUME"] = g["volume"] / g["volume"].rolling(20).mean()
        out_frames.append(g)
    df2 = pd.concat(out_frames, ignore_index=True)
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
