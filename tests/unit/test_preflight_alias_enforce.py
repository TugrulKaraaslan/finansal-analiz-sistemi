from pathlib import Path

import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters


def _setup() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame({"close": [1]})
    filters_df = pd.DataFrame(
        [{"FilterCode": "F1", "PythonQuery": "SMA50 > 0"}]
    )
    return filters_df, df


def test_alias_forbid() -> None:
    filters_df, df = _setup()
    with pytest.raises(SystemExit):
        validate_filters(filters_df, df, alias_mode="forbid")


def test_alias_warn() -> None:
    filters_df, df = _setup()
    with pytest.warns(UserWarning):
        validate_filters(filters_df, df, alias_mode="warn")
