import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import report_utils


def _sample():
    summary = pd.DataFrame({
        "filtre_kodu": ["F1"],
        "ort_getiri_%": [1.0],
        "sebep_kodu": ["OK"],
    })
    detail = pd.DataFrame({
        "filtre_kodu": ["F1"],
        "hisse_kodu": ["AAA"],
        "getiri_yuzde": [1.0],
        "basari": ["BAŞARILI"],
    })
    return summary, detail


def test_build_ozet_df_default_columns():
    summary, detail = _sample()
    df = report_utils.build_ozet_df(summary, detail, "01.01.2025", "02.01.2025")
    assert list(df.columns) == report_utils.DEFAULT_OZET_COLS


def test_build_detay_df_default_columns():
    summary, detail = _sample()
    df = report_utils.build_detay_df(summary, detail, strateji="S1")
    assert list(df.columns) == report_utils.DEFAULT_DETAY_COLS


def test_build_stats_df_default_columns():
    summary, detail = _sample()
    ozet = report_utils.build_ozet_df(summary, detail)
    stats = report_utils.build_stats_df(ozet)
    assert list(stats.columns) == report_utils.DEFAULT_STATS_COLS
