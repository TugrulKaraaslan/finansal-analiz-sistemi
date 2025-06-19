import filter_engine
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_no_stock_reason_for_empty_result():
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [10],
        }
    )
    filters = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 100"]})

    result, _ = filter_engine.uygula_filtreler(df, filters, pd.Timestamp("2025-03-01"))
    assert result["F1"]["sebep"] == "NO_STOCK"
    assert result["F1"]["hisse_sayisi"] == 0


def test_volume_tl_generated_if_missing():
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [10],
            "volume": [5],
        }
    )
    filters = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["volume_tl > 0"]})

    result, _ = filter_engine.uygula_filtreler(df, filters, pd.Timestamp("2025-03-01"))
    assert result["F1"]["sebep"] == "OK"
    assert result["F1"]["hisse_sayisi"] == 1


def test_apply_single_filter_ok():
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [1],
        }
    )
    secim, info = filter_engine._apply_single_filter(df, "T1", "close > 0")
    assert info["durum"] == "OK"
    assert info["secim_adedi"] == 1


def test_apply_single_filter_missing_column():
    df = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [1],
        }
    )
    secim, info = filter_engine._apply_single_filter(df, "T1", "olmayan_kolon < 10")
    assert info["durum"] == "CALISTIRILAMADI"
    assert "olmayan_kolon" in info["eksik_sutunlar"]
