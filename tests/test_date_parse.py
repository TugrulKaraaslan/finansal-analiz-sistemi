"""Unit tests for date_parse."""

import pandas as pd

from utils.date_utils import parse_date


def test_parse_date_variants():
    """Ensure ``parse_date`` handles multiple common formats."""
    cases = {
        "07.03.2025": "2025-03-07",
        "2025-03-07": "2025-03-07",
        "07/03/25": "2025-03-07",
        "2025/03/07": "2025-03-07",
        "20250307": "2025-03-07",
        20250307.0: "2025-03-07",
        "\u00e7\u00f6p": pd.NaT,
    }
    for raw, expected in cases.items():
        ts = parse_date(raw)
        if expected is pd.NaT:
            assert ts is pd.NaT
        else:
            assert ts.strftime("%Y-%m-%d") == expected
