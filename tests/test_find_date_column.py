import pandas as pd

from finansal_analiz_sistemi.data_loader import (
    DATE_COLUMN_CANDIDATES,
    _find_date_column,
)


def test_find_date_column_matches_candidates():
    for col in DATE_COLUMN_CANDIDATES:
        df = pd.DataFrame({col: ["2025-03-07"]})
        assert _find_date_column(df) == col


def test_find_date_column_identifies_unnamed_column():
    df = pd.DataFrame({"a": [1], "Unnamed: 3": ["2025-03-07"]})
    assert _find_date_column(df) == "Unnamed: 3"


def test_find_date_column_ignores_non_date_unnamed_columns():
    df = pd.DataFrame(
        {
            "Unnamed: 0": [1, 2],
            "Unnamed: 3": ["2025-03-07", "2025-03-08"],
        }
    )
    assert _find_date_column(df) == "Unnamed: 3"


def test_find_date_column_returns_none():
    df = pd.DataFrame({"x": [1]})
    assert _find_date_column(df) is None
