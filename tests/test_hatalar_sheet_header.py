"""Tests verifying the header layout of saved error sheets."""

from pathlib import Path

import pandas as pd

import report_generator
from finansal_analiz_sistemi.report_generator import save_hatalar_excel


def test_hatalar_sheet_header(tmp_path: Path) -> None:
    """Ensure saved error sheets use the expected column header order."""
    df = pd.DataFrame(
        {
            "filtre_kod": ["TST1"],
            "hata_tipi": ["QUERY_ERROR"],
            "eksik_ad": ["dummy"],
            "detay": ["detail"],
            "cozum_onerisi": ["fix"],
        }
    )
    out = tmp_path / "out.xlsx"
    save_hatalar_excel(df, out)

    read = pd.read_excel(out, sheet_name="Hatalar")
    assert list(read.columns[:5]) == [
        "filtre_kod",
        "hata_tipi",
        "eksik_ad",
        "detay",
        "cozum_onerisi",
    ]


def generate_excel_with_errors(tmp_path: Path) -> Path:
    """Create an Excel file containing error records."""
    errs = [
        {
            "filtre_kod": "E1",
            "hata_tipi": "QUERY_ERROR",
            "detay": "demo",
            "cozum_onerisi": "fix",
        }
    ]
    summary = pd.DataFrame(columns=report_generator.LEGACY_SUMMARY_COLS)
    detail = pd.DataFrame(columns=report_generator.LEGACY_DETAIL_COLS)
    out = tmp_path / "errs.xlsx"
    report_generator.generate_full_report(summary, detail, errs, out, keep_legacy=True)
    return out


def test_hatalar_sheet_has_filter_ids(tmp_path: Path) -> None:
    """Exported error sheets should retain filter identifiers."""
    xlsx = generate_excel_with_errors(tmp_path)
    df = pd.read_excel(xlsx, sheet_name="Hatalar")
    assert df["filtre_kod"].notna().all()
