"""Unit tests for failed_reason_hint."""

import pandas as pd

import filter_engine
from report_generator import (
    LEGACY_DETAIL_COLS,
    LEGACY_SUMMARY_COLS,
    generate_full_report,
)
from utils.failure_tracker import failures


def _generate_failure():
    """Test _generate_failure."""
    df = pd.DataFrame({"x": [1]})
    filter_engine._apply_single_filter(df, "T0", "0/0")


def _build_report(tmp_path):
    """Test _build_report."""
    out = tmp_path / "fail.xlsx"
    summary = pd.DataFrame(columns=LEGACY_SUMMARY_COLS)
    detail = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    generate_full_report(summary, detail, [], out)
    return pd.read_excel(out, "filters_failed")


def test_reason_hint_filled(tmp_path):
    """Test test_reason_hint_filled."""
    failures.clear()
    _generate_failure()
    df = _build_report(tmp_path)
    assert df[["reason", "hint"]].notna().all(axis=None)
