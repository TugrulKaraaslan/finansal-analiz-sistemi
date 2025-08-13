from types import SimpleNamespace

import pandas as pd
import pytest

from backtest.reporter import write_reports
from backtest.validator import dataset_summary, quality_warnings


def test_dataset_summary_invalid_type():
    with pytest.raises(TypeError):
        dataset_summary([])  # not a DataFrame


def test_dataset_summary_missing_columns():
    df = pd.DataFrame({"symbol": ["AAA"], "close": [1.0]})
    with pytest.raises(ValueError):
        dataset_summary(df)


def test_quality_warnings_missing_columns():
    df = pd.DataFrame({"symbol": ["AAA"], "close": [1.0]})
    with pytest.raises(ValueError):
        quality_warnings(df)


def test_quality_warnings_extra_checks():
    df = pd.DataFrame(
        {
            "symbol": ["AAA"] * 5,
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ]
            ),
            "open": [1.0, 1.0, 1.0, None, 1.0],
            "high": [2.0, 2.0, 0.5, 2.0, 2.0],
            "low": [1.0, 1.0, 1.0, 1.0, 3.0],
            "close": [1.0, 1.0, 1.0, 1.0, float("nan")],
            "volume": [100, 0, 100, 100, -5],
        }
    )
    issues = quality_warnings(df)
    assert set(issues["issue"]) == {
        "non_positive_volume",
        "high_lt_low",
        "na_open",
        "na_close",
    }


class _DummyWriter:
    def __init__(self, *args, **kwargs):
        self.book = SimpleNamespace(add_format=lambda *a, **k: None)
        self.sheets = {}

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        return False


def test_write_reports_xu100_pct_type(monkeypatch):
    monkeypatch.setattr(pd, "ExcelWriter", _DummyWriter)
    monkeypatch.setattr(pd.DataFrame, "to_excel", lambda *a, **k: None)
    trades = pd.DataFrame(
        columns=[
            "FilterCode",
            "Symbol",
            "Date",
            "EntryClose",
            "ExitClose",
            "ReturnPct",
            "Win",
            "Reason",
        ]
    )
    with pytest.raises(TypeError):
        write_reports(
            trades, [], pd.DataFrame(), xu100_pct=[1, 2], out_xlsx="dummy.xlsx"
        )
