import pytest
import pandas as pd

from backtest.calendars import (
    add_next_close,
    add_next_close_calendar,
    build_trading_days,
    load_holidays_csv,
)


def test_add_next_close_invalid_inputs():
    with pytest.raises(TypeError):
        add_next_close([])
    df_missing = pd.DataFrame({"symbol": ["A"], "date": [pd.Timestamp("2020-01-01")]} )
    with pytest.raises(ValueError):
        add_next_close(df_missing)


def test_add_next_close_calendar_invalid_inputs():
    df = pd.DataFrame({"symbol": ["A"], "date": [pd.Timestamp("2020-01-01")], "close": [1.0]})
    with pytest.raises(TypeError):
        add_next_close_calendar([], pd.DatetimeIndex([]))
    with pytest.raises(TypeError):
        add_next_close_calendar(df, ["2020-01-02"])
    with pytest.raises(ValueError):
        add_next_close_calendar(df.drop(columns=["close"]), pd.DatetimeIndex([]))


def test_build_trading_days_invalid_holidays():
    df = pd.DataFrame({"symbol": ["A"], "date": [pd.Timestamp("2020-01-01")]})
    with pytest.raises(TypeError):
        build_trading_days(df, holidays=123)


def test_load_holidays_csv_validation(tmp_path):
    with pytest.raises(TypeError):
        load_holidays_csv(123)
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        load_holidays_csv(missing)
    csv_file = tmp_path / "hol.csv"
    csv_file.write_text("col\n1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_holidays_csv(csv_file)
