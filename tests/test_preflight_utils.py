import pandas as pd

from utils.preflight import canonical, preflight_check, smart_parse_dates


def test_smart_parse_dates_handles_iso_and_tr():
    s = pd.Series(["2025-03-07", "07.03.2025", "07/03/2025", "bad"])
    parsed = smart_parse_dates(s)
    assert parsed[0] == pd.Timestamp("2025-03-07")
    assert parsed[1] == pd.Timestamp("2025-03-07")
    assert parsed[2] == pd.Timestamp("2025-03-07")
    assert pd.isna(parsed[3])


def test_preflight_check_counts_rows_and_missing_columns():
    df = pd.DataFrame(
        {
            "Date": ["07.03.2025", "06.03.2025"],
            "SMA 10": [1.0, 2.0],
            "ADX 14": [1.0, 2.0],
        }
    )
    result = preflight_check(df)
    assert result["rows_on_target"] == 1
    assert result["missing_required_cols"] == ["sma_50"]


def test_canonical_handles_uppercase_dotted_i_sequences():
    """Multiple Turkish 'İ' characters should collapse without underscores."""
    assert canonical("İİ") == "ii"
