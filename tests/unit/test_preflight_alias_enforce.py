from pathlib import Path

import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters
from io_filters import read_filters_file


def _setup(tmp_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame({"close": [1]})
    filters_path = tmp_path / "filters.csv"
    content = "FilterCode;PythonQuery\nF1;SMA50 > 0\n"
    filters_path.write_text(content, encoding="utf-8")
    filters_df = read_filters_file(filters_path)
    return filters_df, df


def test_alias_forbid(tmp_path: Path) -> None:
    filters_df, df = _setup(tmp_path)
    with pytest.raises(SystemExit):
        validate_filters(filters_df, df, alias_mode="forbid")


def test_alias_warn(tmp_path: Path) -> None:
    filters_df, df = _setup(tmp_path)
    with pytest.warns(UserWarning):
        validate_filters(filters_df, df, alias_mode="warn")
