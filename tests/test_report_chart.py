import os
import sys

import openpyxl

import report_utils

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_add_bar_chart():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["filtre", "val"])
    for i in range(1, 6):
        ws.append([f"F{i}", i])
    report_utils.add_bar_chart(ws, data_idx=2, label_idx=1, title="demo")
    assert len(ws._charts) > 0
    wb.close()
