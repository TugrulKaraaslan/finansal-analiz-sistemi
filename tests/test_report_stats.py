"""Test module for test_report_stats."""

import os
import sys

import pandas as pd

import report_stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def sample_data():
    """Test sample_data."""
    summary = pd.DataFrame(
        {
            "filtre_kodu": ["F1", "F2"],
            "ort_getiri_%": [5.0, -3.0],
            "sebep_kodu": ["OK", "NO_STOCK"],
        }
    )
    detail = pd.DataFrame(
        {
            "filtre_kodu": ["F1", "F1"],
            "hisse_kodu": ["AAA", "BBB"],
            "getiri_yuzde": [5.0, 6.0],
            "basari": ["BAŞARILI", "BAŞARILI"],
        }
    )
    return summary, detail


def test_build_ozet_df_columns():
    """Test test_build_ozet_df_columns."""
    summary, detail = sample_data()
    df = report_stats.build_ozet_df(summary, detail, "01.01.2025", "02.01.2025")
    expected = [
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
    ]
    assert list(df.columns) == expected
    assert df.loc[0, "islemli"] == "EVET"


def test_build_detay_df_merges_sebep():
    """Test test_build_detay_df_merges_sebep."""
    summary, detail = sample_data()
    det = report_stats.build_detay_df(summary, detail, strateji="S")
    assert "sebep_kodu" in det.columns
    assert det.loc[0, "strateji"] == "S"


def test_build_stats_df_basic():
    """Test test_build_stats_df_basic."""
    summary, detail = sample_data()
    ozet = report_stats.build_ozet_df(summary, detail)
    stats = report_stats.build_stats_df(ozet)
    assert stats.iloc[0]["toplam_filtre"] == 2
    assert stats.iloc[0]["islemli"] == 1


def test_plot_summary_stats_returns_fig():
    """Test test_plot_summary_stats_returns_fig."""
    summary, detail = sample_data()
    ozet = report_stats.build_ozet_df(summary, detail)
    fig = report_stats.plot_summary_stats(ozet, detail, std_threshold=10)
    assert len(fig.data) == 4


def test_plot_summary_stats_with_processed_detail():
    """Test test_plot_summary_stats_with_processed_detail."""
    summary, detail = sample_data()
    ozet = report_stats.build_ozet_df(summary, detail)
    processed = report_stats.build_detay_df(summary, detail)
    fig = report_stats.plot_summary_stats(ozet, processed, std_threshold=10)
    assert len(fig.data) == 4
