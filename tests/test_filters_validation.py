import pytest
from io_filters import load_filters_csv
from lib.validator import validate_filters


def test_validate_filters_ok():
    df = validate_filters("tests/data/filters_valid.csv")
    assert list(df.columns) == ["filter_name", "query", "group"]
    assert len(df) == 2


def test_validate_filters_empty_query():
    with pytest.raises(ValueError):
        validate_filters("tests/data/filters_empty.csv")


def test_load_filters_missing_column():
    with pytest.raises(RuntimeError):
        load_filters_csv("tests/data/filters_missing_col.csv")
