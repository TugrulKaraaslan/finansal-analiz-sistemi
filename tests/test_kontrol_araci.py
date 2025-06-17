import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import kontrol_araci


def test_tarama_denetimi_collects_info():
    df_filtreler = pd.DataFrame({
        "kod": ["F1", "F2"],
        "PythonQuery": ["close > 10", "open > 5"],
    })

    df_indikator = pd.DataFrame({
        "hisse_kodu": ["AAA"],
        "tarih": [pd.Timestamp("2025-03-01")],
        "close": [5],
    })

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
