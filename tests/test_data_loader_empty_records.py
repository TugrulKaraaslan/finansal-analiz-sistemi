import importlib.util

import pandas as pd
import pytest

from backtest.data_loader import apply_corporate_actions, read_excels_long


def test_read_excels_long_no_valid_sheets(tmp_path):
    # Create an Excel file with an empty sheet and a sheet without a date
    # column
    f = tmp_path / "dummy.xlsx"
    with pd.ExcelWriter(f) as writer:
        # empty sheet
        pd.DataFrame().to_excel(writer, sheet_name="Empty", index=False)
        # sheet missing required 'date' column
        pd.DataFrame({"close": [1]}).to_excel(
            writer, sheet_name="NoDate", index=False)

    df = read_excels_long(tmp_path)
    expected = ["date", "open", "high", "low", "close", "volume", "symbol"]
    assert df.empty
    assert list(df.columns) == expected

    # downstream operations should accept the empty dataframe without errors
    df2 = apply_corporate_actions(df)
    assert df2.empty
    assert list(df2.columns) == expected


def test_read_excels_long_engine_missing(monkeypatch, tmp_path):
    f = tmp_path / "dummy.xlsx"
    with pd.ExcelWriter(f) as writer:
        pd.DataFrame({"date": ["2024-01-01"], "close": [1]}).to_excel(
            writer, index=False
        )

    def _no_engine(name):
        return None

    monkeypatch.setattr(importlib.util, "find_spec", _no_engine)
    with pytest.raises(ImportError):
        read_excels_long(tmp_path, engine="auto")
