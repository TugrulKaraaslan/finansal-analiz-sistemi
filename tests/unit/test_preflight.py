import pandas as pd

from backtest.filters.preflight import validate_filters
from io_filters import read_filters_file


def test_preflight_ok(tmp_path):
    df = pd.DataFrame({"close": [1], "volume": [2]})
    filters_df = read_filters_file("tests/data/filters_valid.csv")
    validate_filters(filters_df, df)
