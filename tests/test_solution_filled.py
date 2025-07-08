"""Test module for test_solution_filled."""

import os
import sys

import pandas as pd

from report_generator import (
    LEGACY_DETAIL_COLS,
    LEGACY_SUMMARY_COLS,
    generate_full_report,
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_solution_not_empty(tmp_path):
    """Test test_solution_not_empty."""
    errs = [
        {
            "filtre_kodu": "T500",
            "hata_tipi": "GENERIC",
            "detay": "Tan\u0131ms\u0131z s\u00fctun/de\u011fi\u015fken: 'df'.",
            "cozum_onerisi": '"df" s\u00fctununu veri setine ekleyin veya sorgudan \u00e7\u0131kar\u0131n.',
        }
    ]
    df_sum = pd.DataFrame(columns=LEGACY_SUMMARY_COLS)
    df_det = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    path = tmp_path / "x.xlsx"
    generate_full_report(df_sum, df_det, errs, path, keep_legacy=True)
    hatalar = pd.read_excel(path, "Hatalar")
    assert (
        hatalar.loc[0, "cozum_onerisi"] != ""
    ), "\u00c7\u00f6z\u00fcm \u00f6nerisi bo\u015f!"
