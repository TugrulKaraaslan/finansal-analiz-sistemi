import pandas as pd
import pytest

from backtest.filters.preflight import validate_filters
from backtest.preflight import UnknownSeriesError, check_unknown_series


def _excel_dir(tmp_path):
    d = tmp_path / "Veri"
    d.mkdir()
    pd.DataFrame({"close": [1]}).to_excel(d / "AAA.xlsx", index=False)
    return d


def test_alias_denied(tmp_path):
    excel_dir = _excel_dir(tmp_path)
    filters = tmp_path / "filters.csv"
    filters.write_text(
        "FilterCode;PythonQuery\nF;its_9>0\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as excinfo:
        validate_filters(filters, excel_dir, alias_mode="forbid")
    assert "Legacy aliases" in str(excinfo.value)


def test_unknown_denied(tmp_path):
    excel_dir = _excel_dir(tmp_path)
    filters = tmp_path / "filters.csv"
    filters.write_text(
        "FilterCode;PythonQuery\nF;unknown_col>0\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as excinfo:
        validate_filters(
            filters,
            excel_dir,
            alias_mode="forbid",
            allow_unknown=False,
        )
    assert "unknown tokens" in str(excinfo.value)


def test_unknown_series_suggestion():
    df = pd.DataFrame({"close": [1]})
    with pytest.raises(UnknownSeriesError) as excinfo:
        check_unknown_series(df, ["cloze>0"])
    assert "did you mean close" in str(excinfo.value)
