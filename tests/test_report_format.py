"""Unit tests covering Excel report layout and legacy column support.

These checks guard against accidental format regressions in generated
workbooks.
"""

import os
import sys

import pandas as pd

from report_generator import (
    LEGACY_DETAIL_COLS,
    LEGACY_SUMMARY_COLS,
    generate_full_report,
)

# Add the project root to ``PYTHONPATH`` for CI runners.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_legacy_columns_preserved(tmp_path):
    """Generated report should keep the legacy column layout."""
    path = tmp_path / "rapor.xlsx"
    summary = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "hisse_sayisi": [1],
            "ort_getiri_%": [1.0],
            "en_yuksek_%": [1.5],
            "en_dusuk_%": [-0.5],
            "islemli": [1],
            "sebep_kodu": ["OK"],
            "sebep_aciklama": [""],
            "tarama_tarihi": ["01.01.2025"],
            "satis_tarihi": ["02.01.2025"],
        }
    )
    detail = pd.DataFrame(
        {
            "filtre_kodu": ["F1"],
            "hisse_kodu": ["AAA"],
            "getiri_%": [1.0],
            "basari": ["BAŞARILI"],
            "strateji": ["S1"],
            "sebep_kodu": ["OK"],
        }
    )
    errors = [
        {"filtre_kodu": "F2", "hata_tipi": "GENERIC", "detay": "x", "cozum_onerisi": ""}
    ]
    generate_full_report(
        summary,
        detail,
        errors,
        path,
        keep_legacy=True,
    )
    with pd.ExcelFile(path) as xls:
        assert xls.sheet_names[:2] == ["Özet", "Detay"]
        assert list(pd.read_excel(xls, "Özet").columns) == LEGACY_SUMMARY_COLS
        assert list(pd.read_excel(xls, "Detay").columns) == LEGACY_DETAIL_COLS
        assert len(pd.read_excel(xls, "Özet")) >= 1
        assert len(pd.read_excel(xls, "Detay")) >= 1
        assert "Hatalar" in xls.sheet_names, "Hatalar sayfası eksik!"
        assert not pd.read_excel(xls, "Hatalar").empty, "Hatalar sayfası boş!"


def test_error_sheet_not_empty(tmp_path):
    """Error sheet must contain rows when a list is provided."""
    # add a dummy QUERY_ERROR row
    errs = [
        {
            "filtre_kodu": "T999",
            "hata_tipi": "QUERY_ERROR",
            "detay": "demo",
            "cozum_onerisi": "fix",
        }
    ]
    path = tmp_path / "r.xlsx"
    generate_full_report(
        pd.DataFrame(columns=LEGACY_SUMMARY_COLS),
        pd.DataFrame(columns=LEGACY_DETAIL_COLS),
        errs,
        path,
        keep_legacy=True,
    )
    assert not pd.read_excel(path, "Hatalar").empty
