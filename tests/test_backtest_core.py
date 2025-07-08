"""Unit tests for backtest_core."""

import os
import sys
import types

import pandas as pd

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # isort: off

import backtest_core  # noqa: E402

sys.modules.setdefault("pandas_ta", types.SimpleNamespace(Strategy=lambda **kw: None))


def test_bireysel_performanslar_contains_new_keys():
    """Report frames should include new performance columns."""
    df = pd.DataFrame(
        {
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
        }
    )
    filtre_sonuc = {"F1": {"hisseler": ["AAA"], "sebep": "OK", "hisse_sayisi": 1}}
    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        filtre_sonuc, df, satis_tarihi_str="10.03.2025", tarama_tarihi_str="07.03.2025"
    )
    assert set(rapor_df.columns) == {"filtre_kodu", "ort_getiri_%", "sebep_kodu"}
    assert {"filtre_kodu", "hisse_kodu", "getiri_yuzde", "basari"}.issubset(
        detay_df.columns
    )
    assert detay_df.iloc[0]["basari"] == "BAŞARILI"


def test_missing_buy_price_sets_data_gap():
    """Fallback to nearby date when the buy price is missing."""
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.to_datetime("10.03.2025", dayfirst=True)],
            "close": [12.5],
        }
    )
    filtre_sonuc = {"F1": {"hisseler": ["AAA"], "sebep": "OK", "hisse_sayisi": 1}}
    rapor_df, detay_df = backtest_core.calistir_basit_backtest(
        filtre_sonuc,
        df,
        satis_tarihi_str="10.03.2025",
        tarama_tarihi_str="07.03.2025",
    )
    row = rapor_df.iloc[0]
    assert row["sebep_kodu"] == "OK"
    assert pd.notna(row["ort_getiri_%"])
