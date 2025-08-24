from __future__ import annotations
"""Convert comma-separated filter CSV to semicolon-separated format."""

import csv
import sys
from pathlib import Path


def migrate(src: str, dst: str) -> None:
    src_path = Path(src)
    dst_path = Path(dst)
    with src_path.open(encoding="utf-8", newline="") as f_in:
        reader = csv.reader(f_in, delimiter=",")
        rows = list(reader)
    with dst_path.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out, delimiter=";")
        writer.writerows(rows)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("kullanim: python tools/migrate_filters_csv.py input.csv output.csv")
        raise SystemExit(1)
    migrate(sys.argv[1], sys.argv[2])
