import pandas as pd
from report_generator import (
    generate_full_report,
    LEGACY_SUMMARY_COLS,
    LEGACY_DETAIL_COLS,
)


def test_legacy_columns_preserved(tmp_path):
    path = tmp_path / "rapor.xlsx"
    generate_full_report(
        pd.DataFrame(columns=LEGACY_SUMMARY_COLS),
        pd.DataFrame(columns=LEGACY_DETAIL_COLS),
        [],
        path,
        keep_legacy=True,
    )
    xls = pd.ExcelFile(path)
    assert xls.sheet_names[:2] == ["Özet", "Detay"]
    assert list(pd.read_excel(xls, "Özet").columns)  == LEGACY_SUMMARY_COLS
    assert list(pd.read_excel(xls, "Detay").columns) == LEGACY_DETAIL_COLS
