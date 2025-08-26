import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters
from backtest.preflight import UnknownSeriesError, check_unknown_series
from io_filters import read_filters_file


def _dataset_df() -> pd.DataFrame:
    return pd.DataFrame({"close": [1]})


def test_alias_denied(tmp_path):
    df = _dataset_df()
    filters = tmp_path / "filters.csv"
    filters.write_text(
        "FilterCode;PythonQuery\nF;SMA50>0\n",
        encoding="utf-8",
    )
    filters_df = read_filters_file(filters)
    with pytest.raises(SystemExit) as excinfo:
        validate_filters(filters_df, df, alias_mode="forbid")
    assert "Legacy aliases" in str(excinfo.value)


def test_unknown_denied(tmp_path):
    df = _dataset_df()
    filters = tmp_path / "filters.csv"
    filters.write_text(
        "FilterCode;PythonQuery\nF;unknown_col>0\n",
        encoding="utf-8",
    )
    filters_df = read_filters_file(filters)
    with pytest.raises(SystemExit) as excinfo:
        validate_filters(
            filters_df,
            df,
            alias_mode="forbid",
            allow_unknown=False,
        )
    assert "unknown tokens" in str(excinfo.value)


def test_unknown_series_suggestion():
    df = pd.DataFrame({"close": [1]})
    with pytest.raises(UnknownSeriesError) as excinfo:
        check_unknown_series(df, ["cloze>0"])
    assert "did you mean close" in str(excinfo.value)
