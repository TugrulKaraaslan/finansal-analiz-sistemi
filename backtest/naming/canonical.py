from __future__ import annotations

# Fiyat alanları ve çekirdek indikatörler (Aşama-1 kapsamı)
CANONICAL_BASE = {
    # price fields
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap_d",
    # moving averages & momentum
    "sma_20",
    "ema_50",
    "wma_20",
    "rsi_14",
    # macd triplet
    "macd_12_26_9",
    "macd_signal_12_26_9",
    "macd_hist_12_26_9",
    # bollinger
    "bbl_20_2",
    "bbm_20_2",
    "bbh_20_2",
    # directional movement
    "adx_14",
    "dmp_14",
    "dmn_14",
    # aroon
    "aroon_up_14",
    "aroon_down_14",
    # stochrsi (varsayılan param seti)
    "stochrsi_k_14_14_3",
    "stochrsi_d_14_14_3",
    # changes & volume derived
    "change_1d_percent",
    "change_1w_percent",
    "relative_volume",
}

# İleride ekleme bu set üzerinden yapılır
CANONICAL_SET = set(CANONICAL_BASE)
