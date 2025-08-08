import pandas as pd
import pytest

from backtest.data_loader import validate_columns


def test_validate_columns_missing():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        validate_columns(df, ["a", "b"])
