from pathlib import Path

import pytest

from io_filters import load_filters_csv

DATA_DIR = Path(__file__).resolve().parent / "data"


def test_load_filters_ok(tmp_path):
    p = tmp_path / "filters.csv"
    p.write_text("FilterCode;PythonQuery\nf1;close>0\nf2;volume>0\n", encoding="utf-8")
    rows = load_filters_csv([p])
    assert len(rows) == 2


def test_load_filters_empty_query():
    with pytest.raises(ValueError):
        load_filters_csv([DATA_DIR / "filters_empty.csv"])


def test_load_filters_missing_column():
    with pytest.raises(ValueError):
        load_filters_csv([DATA_DIR / "filters_missing_col.csv"])


def test_load_filters_semicolon(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text("FilterCode;PythonQuery\nF1;close>0\n", encoding="utf-8")
    rows = load_filters_csv([csv_file])
    assert rows[0]["FilterCode"] == "F1"


def test_load_filters_parse_error(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text('FilterCode;PythonQuery\n"unclosed', encoding="utf-8")
    with pytest.raises(ValueError):
        load_filters_csv([csv_file])


def test_load_filters_duplicate_codes(tmp_path):
    csv_file = tmp_path / "filters.csv"
    csv_file.write_text("FilterCode;PythonQuery\nF1;close>0\nF1;close>1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_filters_csv([csv_file])
