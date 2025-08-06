import pandas as pd
import pytest
from types import SimpleNamespace

from backtest.validator import dataset_summary, quality_warnings
from backtest.reporter import write_reports


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


class _DummyWriter:
    def __init__(self, *args, **kwargs):
        self.book = SimpleNamespace(add_format=lambda *a, **k: None)
        self.sheets = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
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
        ]
    )
    with pytest.raises(TypeError):
        write_reports(trades, [], pd.DataFrame(), xu100_pct=[1, 2], out_xlsx="dummy.xlsx")
