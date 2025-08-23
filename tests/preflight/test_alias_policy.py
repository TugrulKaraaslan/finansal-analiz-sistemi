import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters


def _excel_dir(tmp_path):
    d = tmp_path / "Veri"
    d.mkdir()
    pd.DataFrame({"close": [1]}).to_excel(d / "AAA.xlsx", index=False)
    return d


def test_alias_denied(tmp_path):
    excel_dir = _excel_dir(tmp_path)
    filters = tmp_path / "filters.csv"
    filters.write_text("FilterCode;PythonQuery\nF;its_9>0\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        validate_filters(filters, excel_dir, alias_mode="forbid")


def test_unknown_denied(tmp_path):
    excel_dir = _excel_dir(tmp_path)
    filters = tmp_path / "filters.csv"
    filters.write_text("FilterCode;PythonQuery\nF;unknown_col>0\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        validate_filters(filters, excel_dir, alias_mode="forbid", allow_unknown=False)
