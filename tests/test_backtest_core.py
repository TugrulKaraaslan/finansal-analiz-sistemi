import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import types

sys.modules.setdefault('pandas_ta', types.SimpleNamespace(Strategy=lambda **kw: None))
import backtest_core
import config


def test_bireysel_performanslar_contains_new_keys():
    df = pd.DataFrame({
        "hisse_kodu": ["AAA", "AAA"],
        "tarih": [
            pd.to_datetime("07.03.2025", dayfirst=True),
            pd.to_datetime("10.03.2025", dayfirst=True),
        ],
        "open": [10, 12],
        "high": [11, 13],
        "low": [9, 11],
        "close": [10.5, 12.5],
        "volume": [1000, 1100],
    })
    filtrelenmis = {"F1": ["AAA"]}
    results, _ = backtest_core.calistir_basit_backtest(
        filtrelenmis,
        df,
        satis_tarihi_str="10.03.2025",
        tarama_tarihi_str="07.03.2025"
    )
    perf_df = results["F1"]["hisse_performanslari"]
    assert {"alis_tarihi", "satis_tarihi", "uygulanan_strateji"}.issubset(perf_df.columns)
    row = perf_df.iloc[0]
    assert row["alis_tarihi"] == "07.03.2025"
    assert row["satis_tarihi"] == "10.03.2025"
    assert row["uygulanan_strateji"] == config.UYGULANAN_STRATEJI


def test_missing_close_column_skips_stock():
    df = pd.DataFrame({
        "hisse_kodu": ["AAA", "AAA"],
        "tarih": [
            pd.to_datetime("07.03.2025", dayfirst=True),
            pd.to_datetime("10.03.2025", dayfirst=True),
        ],
        "open": [10, 12],
        "high": [11, 13],
        "low": [9, 11],
        "volume": [1000, 1100],
    })
    filtrelenmis = {"F1": ["AAA"]}
    results, _ = backtest_core.calistir_basit_backtest(
        filtrelenmis,
        df,
        satis_tarihi_str="10.03.2025",
        tarama_tarihi_str="07.03.2025",
    )
    perf_df = results["F1"]["hisse_performanslari"]
    assert perf_df.empty
    assert results["F1"]["islem_yapilan_sayisi"] == 0
    assert pd.isna(results["F1"]["ortalama_getiri"])
