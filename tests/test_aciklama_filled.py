"""Ensure summary rows include descriptive explanations.

Reports should carry forward the ``sebep_aciklama`` text so users can
understand why each filter produced its result.
"""

import os
import sys

import pandas as pd

from report_generator import LEGACY_DETAIL_COLS, generate_full_report

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_aciklama_filled(tmp_path):
    """Summary rows should be populated with explanation text."""
    # one row OK, one QUERY_ERROR
    df_sum = pd.DataFrame(
        [
            ["T1", 1, 1.0, 1, 0, 1, "OK", "", "", ""],
            ["T2", 0, None, None, None, 0, "QUERY_ERROR", "", "", ""],
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
    errs = [
        {
            "filtre_kodu": "T2",
            "hata_tipi": "QUERY_ERROR",
            "detay": "demo hata metni",
            "cozum_onerisi": "düzelt",
        }
    ]
    path = tmp_path / "rapor.xlsx"
    generate_full_report(df_sum, df_det, errs, path, keep_legacy=True)
    with pd.ExcelFile(path) as xls:
        ozet = pd.read_excel(xls, "Özet")
    assert (
        ozet.loc[ozet["filtre_kodu"] == "T2", "sebep_aciklama"].iloc[0]
        == "demo hata metni"
    )


def test_aciklama_dedup(tmp_path):
    """Error descriptions should not duplicate within the summary sheet."""
    df_sum = pd.DataFrame(
        [
            ["T1", 1, 1.0, 1, 0, 1, "OK", "", "", ""],
            ["T2", 0, None, None, None, 0, "QUERY_ERROR", "", "", ""],
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
    errs = [
        {
            "filtre_kodu": "T2",
            "hata_tipi": "QUERY_ERROR",
            "detay": "ilk hata",
            "cozum_onerisi": "düzelt",
        },
        {
            "filtre_kodu": "T2",
            "hata_tipi": "QUERY_ERROR",
            "detay": "ikinci hata",
            "cozum_onerisi": "düzelt",
        },
    ]
    path = tmp_path / "rapor2.xlsx"
    generate_full_report(df_sum, df_det, errs, path, keep_legacy=True)
    with pd.ExcelFile(path) as xls:
        ozet = pd.read_excel(xls, "Özet")
    assert len(ozet) == 2
    assert ozet.loc[ozet["filtre_kodu"] == "T2", "sebep_aciklama"].iloc[0] == "ilk hata"
