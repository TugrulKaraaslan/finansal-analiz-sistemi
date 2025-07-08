"""Unit tests for failed_lists."""

import os
import sys

import openpyxl
import pandas as pd

from report_generator import (
    LEGACY_DETAIL_COLS,
    LEGACY_SUMMARY_COLS,
    generate_full_report,
)
from utils.failure_tracker import failures, log_failure

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_failed_sheets_created(tmp_path):
    """Failure logs should be exported to dedicated worksheets."""
    failures.clear()
    log_failure("filters", "T99", "missing column")
    out = tmp_path / "rep.xlsx"
    summary = pd.DataFrame(columns=LEGACY_SUMMARY_COLS)
    detail = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    generate_full_report(summary, detail, [], out)

    wb = openpyxl.load_workbook(out)
    assert "filters_failed" in wb.sheetnames
    wb.close()
