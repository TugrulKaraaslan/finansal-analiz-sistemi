"""Test module for test_kontrol_araci."""

import os
import sys

import pandas as pd

import src.kontrol_araci as kontrol_araci

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_tarama_denetimi_collects_info():
    """Test test_tarama_denetimi_collects_info."""
    df_filtreler = pd.DataFrame(
        {
            "kod": ["F1", "F2"],
            "PythonQuery": ["close > 10", "open > 5"],
        }
    )

    df_indikator = pd.DataFrame(
        {
            "hisse_kodu": ["AAA"],
            "tarih": [pd.Timestamp("2025-03-01")],
            "close": [5],
        }
    )

    result = kontrol_araci.tarama_denetimi(df_filtreler, df_indikator)

    assert list(result.columns) == [
        "kod",
        "tip",
        "durum",
        "sebep",
        "eksik_sutunlar",
        "nan_sutunlar",
        "secim_adedi",
    ]

    row_f1 = result[result["kod"] == "F1"].iloc[0]
    assert row_f1["durum"] == "BOS"
    assert row_f1["secim_adedi"] == 0

    row_f2 = result[result["kod"] == "F2"].iloc[0]
    assert row_f2["durum"] == "CALISTIRILAMADI"
    assert "open" in row_f2["eksik_sutunlar"]


def test_tarama_denetimi_empty_filters():
    """Test test_tarama_denetimi_empty_filters."""
    df_filtreler = pd.DataFrame(columns=["kod", "PythonQuery"])
    out = kontrol_araci.tarama_denetimi(df_filtreler, pd.DataFrame())
    assert len(out) == 1
    assert out.iloc[0]["kod"] == "_SUMMARY"


def test_tarama_denetimi_filtercode_renamed():
    """Test test_tarama_denetimi_filtercode_renamed."""
    df_filtreler = pd.DataFrame({"FilterCode": ["F1"], "PythonQuery": ["close > 0"]})
    df_ind = pd.DataFrame({"close": [1]})
    out = kontrol_araci.tarama_denetimi(df_filtreler, df_ind)
    assert out.loc[0, "kod"] == "F1"
