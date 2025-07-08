"""Unit tests for header_alignment."""

from finansal_analiz_sistemi.data_loader import load_filter_csv


def test_header_alignment(tmp_path):
    """CSV headers should be normalized to the expected column names."""
    tmp = tmp_path / "15.csv"
    tmp.write_text("dummy\n2025-01-01;MACD;close>vwap\n")

    df = load_filter_csv(tmp)
    assert list(df.columns) == ["tarih", "filtre_kodu", "PythonQuery"]
