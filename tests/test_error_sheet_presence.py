import os
import sys

import pandas as pd
import pytest

from report_generator import LEGACY_DETAIL_COLS, generate_full_report

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


@pytest.fixture
def report_path(tmp_path):
    df_sum = pd.DataFrame(
        [
            ["T1", 1, 2.0, 2, -1, 1, "OK", "", "", ""],
            ["T2", 0, None, None, None, 0, "NO_STOCK", "", "", ""],
            ["T3", 0, None, None, None, 0, "QUERY_ERROR", "", "", ""],
            ["T4", 0, None, None, None, 0, "NO_STOCK", "", "", ""],
            ["T5", 2, 10.0, 15, -2, 1, "OK", "", "", ""],
        ],
        columns=[
            "filtre_kodu",
            "hisse_sayisi",
            "ort_getiri_%",
            "en_yuksek_%",
            "en_dusuk_%",
            "islemli",
            "sebep_kodu",
            "sebep_aciklama",
            "tarama_tarihi",
            "satis_tarihi",
        ],
    )
    df_det = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    err_list = [
        {
            "filtre_kodu": "T3",
            "hata_tipi": "QUERY_ERROR",
            "eksik_ad": "-",
            "detay": "demo parse hatası",
            "cozum_onerisi": "ifade düzelt",
            "reason": "demo",
            "hint": "-",
        }
    ]
    path = tmp_path / "rapor.xlsx"
    generate_full_report(df_sum, df_det, err_list, path, keep_legacy=True)
    return path


def test_error_sheet_presence(report_path):
    xls = pd.ExcelFile(report_path)
    assert "Hatalar" in xls.sheet_names
    df = pd.read_excel(report_path, "Hatalar")
    assert not df.empty
    critical = [
        "hata_tipi",
        "eksik_ad",
        "detay",
        "cozum_onerisi",
        "reason",
        "hint",
    ]
    assert df[critical].notna().all(axis=None)
