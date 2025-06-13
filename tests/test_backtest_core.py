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
    rapor_df, _ = backtest_core.calistir_basit_backtest(
        filtrelenmis,
        df,
        satis_tarihi_str="10.03.2025",
        tarama_tarihi_str="07.03.2025"
    )
    assert set(rapor_df.columns) == {
        "filtre_kodu",
        "hisse_sayisi",
        "islem_yapilan_sayisi",
        "ortalama_getiri",
    }
    row = rapor_df.iloc[0]
    assert row["filtre_kodu"] == "F1"
    assert row["hisse_sayisi"] == 1


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
    rapor_df, _ = backtest_core.calistir_basit_backtest(
        filtrelenmis,
        df,
        satis_tarihi_str="10.03.2025",
        tarama_tarihi_str="07.03.2025",
    )
    row = rapor_df.iloc[0]
    assert row["islem_yapilan_sayisi"] == 0
    assert pd.isna(row["ortalama_getiri"])
