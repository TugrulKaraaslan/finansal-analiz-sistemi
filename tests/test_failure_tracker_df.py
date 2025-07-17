"""Test conversion of failure logs to a DataFrame."""

import utils.failure_tracker as ft


def test_failures_to_df():
    ft.clear_failures()
    ft.log_failure("filters", "T1", "missing")
    ft.log_failure("indicators", "RSI", "calc", "install")
    df = ft.failures_to_df()
    assert list(df.columns) == ["category", "item", "reason", "hint"]
    assert len(df) == 2
    assert df.loc[0, "category"] == "filters"
    assert df.loc[1, "hint"] == "install"
