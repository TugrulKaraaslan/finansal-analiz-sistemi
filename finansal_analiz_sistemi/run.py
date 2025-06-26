import argparse
from pathlib import Path

import pandas as pd

from finansal_analiz_sistemi.report_writer import ReportWriter


def main(argv=None):
    parser = argparse.ArgumentParser(description="Basit rapor üret")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD formatında tarih")
    parser.add_argument("--output", help="Çıktı Excel dosyası")
    args = parser.parse_args(argv)

    df = pd.DataFrame({"tarih": [args.date]})
    out = Path(args.output or f"rapor_{args.date}.xlsx")
    ReportWriter().write_report(df, out)
    print(f"Rapor oluşturuldu -> {out}")


if __name__ == "__main__":
    main()
