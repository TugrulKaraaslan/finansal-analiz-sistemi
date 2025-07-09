"""Verify memory-safe Excel output for large detail sheets."""

import openpyxl
import pandas as pd

import report_generator


def test_detay_sheet_chunked(tmp_path):
    """Large detail sheets should be written in chunks."""
    summary = pd.DataFrame(
        {"filtre_kodu": ["F1"], "ort_getiri_%": [1.0], "sebep_kodu": ["OK"]}
    )
    rows = 200_005
    detail = pd.DataFrame(
        {
            "filtre_kodu": ["F1"] * rows,
            "hisse_kodu": [f"H{i}" for i in range(rows)],
            "getiri_yuzde": [0.5] * rows,
            "basari": ["OK"] * rows,
        }
    )
    out = tmp_path / "mem.xlsx"
    report_generator.generate_full_report(summary, detail, [], out)
    wb = openpyxl.load_workbook(out, read_only=True)
    assert wb["Detay"].max_row == rows + 1
    wb.close()
