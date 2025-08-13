import pytest
from io_filters import load_filters_csv


def test_load_filters_ok():
    df = load_filters_csv("tests/data/filters_valid.csv")
    assert list(df.columns) == ["FilterCode", "PythonQuery", "Group"]
    assert len(df) == 2


def test_load_filters_empty_query():
    with pytest.raises(RuntimeError):
        load_filters_csv("tests/data/filters_empty.csv")


def test_load_filters_missing_column():
    with pytest.raises(RuntimeError):
        load_filters_csv("tests/data/filters_missing_col.csv")


def test_load_filters_semicolon(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text("FilterCode;PythonQuery\nF1;close>0\n", encoding="utf-8")
    df = load_filters_csv(csv_file)
    assert df.loc[0, "FilterCode"] == "F1"


def test_load_filters_parse_error(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text('FilterCode,PythonQuery\n"unclosed', encoding="utf-8")
    with pytest.raises(RuntimeError):
        load_filters_csv(csv_file)


def test_load_filters_duplicate_codes(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text(
        "FilterCode,PythonQuery\nF1,close>0\nF1,close>1\n", encoding="utf-8"
    )
    with pytest.raises(RuntimeError):
        load_filters_csv(csv_file)
