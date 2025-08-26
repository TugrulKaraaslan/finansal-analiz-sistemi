import pandas as pd

from backtest.filters.preflight import validate_filters


def test_preflight_ok():
    df = pd.DataFrame({"close": [1], "volume": [2]})
    filters_df = pd.DataFrame(
        [{"FilterCode": "F1", "PythonQuery": "close>0"}]
    )
    validate_filters(filters_df, df)
