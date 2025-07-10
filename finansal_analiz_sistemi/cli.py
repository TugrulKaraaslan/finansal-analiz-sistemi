"""Minimal command line interface for running reports and validations."""

import atexit
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

# allow running this file directly
if __package__ is None:  # pragma: no cover - safe guard for manual execution
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from finansal_analiz_sistemi.logging_utils import ERROR_COUNTER
from finansal_analiz_sistemi.report_writer import ReportWriter

logger = logging.getLogger(__name__)




def parse_args() -> Namespace:
    """Return parsed arguments for this CLI.

    Parses options controlling report generation and filter validation.
    """
    p = ArgumentParser(description="Rapor üret veya filtreleri doğrula")

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
    p.add_argument(
        "--validate-filters",
        action="store_true",
        help="Sadece filtre tanımlarını doğrula",
    )

    args = p.parse_args()

    if not args.dosya.exists():
        p.error(f"Dosya bulunamadı: {args.dosya}")

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    return args


def run_analysis(csv_path: Path) -> Path:
    """Read CSV and write Excel report next to it."""
    df = pd.read_csv(csv_path, sep=";")
    out_path = csv_path.with_suffix(".xlsx")
    ReportWriter().write_report(df, out_path)
    return out_path


@atexit.register
def _summary() -> None:
    """Log a final summary and exit with error status if needed."""
    logger.info(
        "[SUMMARY] run finished — errors=%d warnings=%d",
        ERROR_COUNTER["errors"],
        ERROR_COUNTER["warnings"],
    )
    if ERROR_COUNTER["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    if args.validate_filters:
        from filtre_dogrulama import validate

        df = pd.read_csv(args.dosya, sep=";")
        errors = validate(df)
        if errors:
            for err in errors:
                print(f"{err.hata_tipi}: {err.detay}")
            sys.exit(2)
        print("Filtreler geçerli ✅")
    else:
        out = run_analysis(args.dosya)
        print(f"Rapor oluşturuldu -> {out}")
