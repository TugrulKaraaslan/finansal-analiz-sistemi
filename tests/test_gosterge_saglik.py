"""Unit tests for gosterge_saglik."""

import os
import sys

from src import kontrol_araci

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_tarama_denetimi_returns_expected_cols(sample_filtreler, sample_indikator_df):
    """Test test_tarama_denetimi_returns_expected_cols."""
    df = kontrol_araci.tarama_denetimi(sample_filtreler, sample_indikator_df)
    expected = {
        "kod",
        "tip",
        "durum",
        "sebep",
        "eksik_sutunlar",
        "nan_sutunlar",
        "secim_adedi",
    }
    assert expected.issubset(df.columns)


def test_at_least_one_error(sample_filtreler, sample_indikator_df):
    """Test test_at_least_one_error."""
    df = kontrol_araci.tarama_denetimi(sample_filtreler, sample_indikator_df)
    assert (df["durum"] != "OK").any(), "En az bir sorun satırı bekleniyordu"
