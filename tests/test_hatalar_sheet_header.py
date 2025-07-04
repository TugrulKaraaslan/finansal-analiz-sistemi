import pandas as pd
from pathlib import Path

from finansal_analiz_sistemi.report_generator import save_hatalar_excel


def test_hatalar_sheet_header(tmp_path: Path) -> None:
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

