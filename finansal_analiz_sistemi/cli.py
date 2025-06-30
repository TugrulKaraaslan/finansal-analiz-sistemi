import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

# allow running this file directly
if __package__ is None:  # pragma: no cover - safe guard for manual execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from finansal_analiz_sistemi.report_writer import ReportWriter


def run_analysis(csv_path: Path) -> Path:
    """Read CSV and write Excel report next to it."""
    df = pd.read_csv(csv_path)
    out_path = csv_path.with_suffix(".xlsx")
    ReportWriter().write_report(df, out_path)
    return out_path


def parse_args() -> Path:
    p = ArgumentParser(description="Rapor üret")

    p.add_argument(
        "--dosya",
        type=Path,
        required=True,
        help="İşlenecek CSV dosyası",
    )
    p.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log seviyesi",
    )

    args = p.parse_args()

    if not args.dosya.exists():
        p.error(f"Dosya bulunamadı: {args.dosya}")

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    return args.dosya


if __name__ == "__main__":
    csv_path = parse_args()
    out = run_analysis(csv_path)
    print(f"Rapor oluşturuldu -> {out}")
