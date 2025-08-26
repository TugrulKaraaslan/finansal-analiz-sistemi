import pandas as pd

from backtest.filters.preflight import validate_filters
from io_filters import read_filters_file


def test_alias_allowed(tmp_path):
    df = pd.DataFrame({"close": [1]})
    f = tmp_path / "filters.csv"
    f.write_text(
        "FilterCode;PythonQuery\nX1;SMA50 > BBU_20_2.0\n",
        encoding="utf-8",
    )
    filters_df = read_filters_file(f)
    validate_filters(filters_df, df, alias_mode="allow", allow_unknown=True)
