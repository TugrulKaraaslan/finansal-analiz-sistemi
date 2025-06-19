import os, sys
import pandas as pd
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from report_generator import generate_full_report, LEGACY_SUMMARY_COLS, LEGACY_DETAIL_COLS
from utils.failure_tracker import log_failure, failures


def test_failed_sheets_created(tmp_path):
    failures.clear()
    log_failure("filters", "T99", "missing column")
    out = tmp_path / "rep.xlsx"
    summary = pd.DataFrame(columns=LEGACY_SUMMARY_COLS)
    detail = pd.DataFrame(columns=LEGACY_DETAIL_COLS)
    generate_full_report(summary, detail, [], out)

    wb = openpyxl.load_workbook(out)
    assert "filters_failed" in wb.sheetnames
    wb.close()
