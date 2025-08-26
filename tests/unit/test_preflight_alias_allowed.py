import pandas as pd

from backtest.filters.preflight import validate_filters


def test_alias_allowed():
    df = pd.DataFrame({"close": [1]})
    filters_df = pd.DataFrame(
        [{"FilterCode": "X1", "PythonQuery": "SMA50 > BBU_20_2.0"}]
    )
    validate_filters(filters_df, df, alias_mode="allow", allow_unknown=True)
