from report_stats import normalize_pct
import os
import sys
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("6", 6.00),
        ("6%", 6.00),
        (600, 6.00),
        ("-450%", -4.50),
    ],
)
def test_normalize_pct(raw, expected):
    result = normalize_pct(pd.Series([raw]))[0]
    assert result == pytest.approx(expected)
