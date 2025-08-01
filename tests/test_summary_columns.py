"""Tests for helper functions that build summary tables."""

from report_generator import generate_summary


def dummy_results():
    """Return example rows for summary column tests."""
    return [
        {"hisse_kodu": "AAA", "getiri_%": 12.3},
        {"hisse_kodu": "BBB", "getiri_%": -3.1},
    ]


EXPECTED_COLUMNS = [
    "hisse_kodu",
    "hisse_sayisi",
    "getiri_%",
    "max_dd_%",
    "giris_tarihi",
    "cikis_tarihi",
    "giris_fiyati",
    "cikis_fiyati",
    "strateji_adi",
    "filtre_kodu",
    "taramada_bulundu",
    "risk_skoru",
    "notlar",
]


def test_summary_columns_complete():
    """Summary DataFrame should include all expected columns."""
    df = generate_summary(dummy_results())
    assert list(df.columns)[:13] == EXPECTED_COLUMNS
