"""Test module for test_empty_summary_warns."""

import logging

import openpyxl
import pandas as pd

import report_generator
from utils.compat import safe_to_excel


def test_generate_summary_warns_on_empty(caplog):
    """Test test_generate_summary_warns_on_empty."""
    with caplog.at_level(logging.WARNING):
        df = report_generator.generate_summary([])
    assert df.empty
    assert "sonuç listesi boş" in caplog.text
    assert (
        list(df.columns)[: len(report_generator.EXPECTED_COLUMNS)]
        == report_generator.EXPECTED_COLUMNS
    )


def test_safe_to_excel_warns(tmp_path, caplog):
    """Test test_safe_to_excel_warns."""
    file = tmp_path / "empty.xlsx"
    with caplog.at_level(logging.WARNING):
        with pd.ExcelWriter(file) as wr:
            safe_to_excel(pd.DataFrame(), wr, sheet_name="Test", index=False)
    assert file.exists()
    assert "boş" in caplog.text
    wb = openpyxl.load_workbook(file)
    assert "Test" in wb.sheetnames
    wb.close()
