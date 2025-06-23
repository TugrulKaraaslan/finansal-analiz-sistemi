"""Paketin tek giriş noktası.

`python -m finansal_analiz_sistemi --tarama …` veya
`from finansal_analiz_sistemi import main; main.main(...)`
ikisi de aynı davranışı gösterir.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from run import calistir_tum_sistemi


def main(
    tarama: str,
    satis: str,
    output: str = "rapor.xlsx",
    log: str | None = None,
) -> None:
    """Tam rapor akışını çalıştır."""
    out_path = Path(output).expanduser().resolve()
    log_path = Path(log).expanduser().resolve() if log else None

    calistir_tum_sistemi(
        tarama_tarihi=tarama,
        satis_tarihi=satis,
        output_path=out_path,
        log_path=log_path,
    )
    print(f"✅ Rapor yazıldı → {out_path}")


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Finansal analiz tam rapor üreticisi"
    )
    parser.add_argument("--tarama", required=True, help="YYYY-MM-DD")
    parser.add_argument("--satis", required=True, help="YYYY-MM-DD")
    parser.add_argument("--output", default="rapor.xlsx")
    parser.add_argument("--log", default=None)
    args = parser.parse_args()
    main(args.tarama, args.satis, args.output, args.log)

