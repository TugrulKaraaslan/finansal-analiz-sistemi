import os
import sys
import pandas as pd
import openpyxl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import report_generator


def test_hatalar_sheet(tmp_path):
    fname = tmp_path / "test.xlsx"
    # create base workbook
    with pd.ExcelWriter(fname) as w:
        pd.DataFrame({"a": [1]}).to_excel(w, sheet_name="Sheet1", index=False)

    atlanmis = {"F1": "err"}
    with pd.ExcelWriter(fname, mode="a", if_sheet_exists="replace", engine="openpyxl") as wr:
        report_generator.olustur_hatali_filtre_raporu(atlanmis, wr)

    wb = openpyxl.load_workbook(fname)
    assert "Hatalar" in wb.sheetnames
    assert wb["Hatalar"].max_row > 1
    wb.close()
