import pandas as pd
import pytest

from io_filters import validate_filters_df


def test_filters_schema_valid():
    df = pd.DataFrame([
        {"FilterCode": "F1", "PythonQuery": "close>1"}
    ])
    out = validate_filters_df(df)
    assert out.iloc[0]["FilterCode"] == "F1"


def test_filters_missing_column():
    df = pd.DataFrame([
        {"FilterCode": "F1", "Foo": 1}
    ])
    with pytest.raises(ValueError):
        validate_filters_df(df)


def test_filters_empty():
    df = pd.DataFrame(columns=["FilterCode", "PythonQuery"])
    with pytest.raises(ValueError):
        validate_filters_df(df)
