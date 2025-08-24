import pandas as pd
import pytest

from io_filters import load_filters_csv, read_filters_csv


def test_filters_semicolon_and_schema(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode;PythonQuery\nF1;close>1\n", encoding="utf-8")
    rows = load_filters_csv([p])
    assert rows[0]["FilterCode"] == "F1"


def test_filters_missing_column(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode;Foo\nF1;1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_filters_csv([p])


def test_filters_wrong_delimiter(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode,PythonQuery\nF1,close>1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="CSV delimiter ';' bekleniyor"):
        read_filters_csv(p)
