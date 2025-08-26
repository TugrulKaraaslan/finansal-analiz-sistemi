import pytest

from io_filters import load_filters_files, read_filters_file


def test_filters_semicolon_and_schema(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode;PythonQuery\nF1;close>1\n", encoding="utf-8")
    rows = load_filters_files([p])
    assert rows[0]["FilterCode"] == "F1"


def test_filters_missing_column(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode;Foo\nF1;1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_filters_files([p])


def test_filters_wrong_delimiter(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode,PythonQuery\nF1,close>1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="';' ayraç bekleniyor"):
        read_filters_file(p)
