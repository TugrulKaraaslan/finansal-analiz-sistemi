"""Smoke tests for :mod:`report_generator` output routines.

These checks verify that a simple DataFrame can be written to Excel using
the high-level ``ReportWriter`` interface.
"""

import pandas as pd

import report_generator


def test_report_file_created(tmp_path):
    """Report generation should create a non-empty Excel file."""
    out = tmp_path / "t.xlsx"
    summary_df = pd.DataFrame(columns=report_generator.LEGACY_SUMMARY_COLS)
    detail_df = pd.DataFrame(columns=report_generator.LEGACY_DETAIL_COLS)
    report_generator.generate_full_report(summary_df, detail_df, [], out)
    assert out.exists() and out.stat().st_size > 0
