"""Test module for test_date_parse."""

import pandas as pd

from utils.date_utils import parse_date


def test_parse_date_variants():
    """Test test_parse_date_variants."""
    cases = {
        "07.03.2025": "2025-03-07",
        "2025-03-07": "2025-03-07",
        "07/03/25": "2025-03-07",
        "\u00e7\u00f6p": pd.NaT,
    }
    for raw, expected in cases.items():
        ts = parse_date(raw)
        if expected is pd.NaT:
            assert ts is pd.NaT
        else:
            assert ts.strftime("%Y-%m-%d") == expected
