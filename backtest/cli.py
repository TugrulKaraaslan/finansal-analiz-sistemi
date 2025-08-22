import argparse
import os
import sys
import logging
import pandas as pd

from backtest.config import load_config, merge_cli_overrides, Flags, setup_logging
from backtest.validation import validate_filters
from backtest.batch import run_scan_range, run_scan_day

logger = logging.getLogger("backtest.cli")


def _file_must_exist(path: str, code: str = "CL002"):
    if not path or not os.path.exists(path):
        print(f"❌ {code}: yol yok/erişilemedi → {path}")
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="backtest", description="Stage1 CLI")
    p.add_argument("--config", default=None, help="YAML config (opsiyonel)")
    p.add_argument("--log-level", default=None, help="DEBUG/INFO/WARNING/ERROR")

    sub = p.add_subparsers(dest="cmd", required=True)

    # dry-run
    pr = sub.add_parser("dry-run", help="filters.csv doğrulama")
    pr.add_argument("--filters", required=True)
    pr.add_argument("--alias", default=None)

    # ortak bayraklar
    def add_common(sp):
        sp.add_argument("--filters", required=True)
        sp.add_argument("--alias", default=None)
        sp.add_argument("--filters-off", action="store_true", help="Filtre uygulamasını kapat")
        sp.add_argument("--no-write", action="store_true", help="Dosya yazma kapalı")

    pd_day = sub.add_parser("scan-day", help="Tek gün tarama")
    pd_day.add_argument("--data", required=True)
    pd_day.add_argument("--date", required=True)
    pd_day.add_argument("--out", required=True)
    add_common(pd_day)

    prange = sub.add_parser("scan-range", help="Tarih aralığı tarama")
    prange.add_argument("--data", required=True)
    prange.add_argument("--start", required=True)
    prange.add_argument("--end", required=True)
    prange.add_argument("--out", required=True)
    add_common(prange)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # config yükle + override
    cfg = load_config(args.config)
    cfg = merge_cli_overrides(
        cfg,
        dry_run=(args.cmd == "dry-run"),
        write_outputs=not getattr(args, "no_write", False),
        filters_enabled=not getattr(args, "filters_off", False),
        log_level=args.log_level,
    )

    setup_logging(cfg.get("cli", {}).get("log_level", "INFO"))
    flags = Flags.from_dict(cfg.get("flags", {}))
    logger.info("flags=%s", flags)

    if args.cmd == "dry-run":
        _file_must_exist(args.filters)
        if args.alias:
            _file_must_exist(args.alias)
        rep = validate_filters(args.filters, args.alias)
        if rep.ok():
            print("✅ Uyum Tam")
            sys.exit(0)
        else:
            for err in rep.errors:
                print(f"❌ Satır {err['row']} | {err['code']} | {err['msg']}")
            for warn in rep.warnings:
                print(f"⚠️ Satır {warn['row']} | {warn['code']} | {warn['msg']}")
            sys.exit(1)

    # ortak veri yükleme
    _file_must_exist(args.data)
    if args.alias:
        _file_must_exist(args.alias)
    _file_must_exist(args.filters)

    # veri yükle
    if args.data.lower().endswith(".parquet"):
        df = pd.read_parquet(args.data)
    else:
        df = pd.read_csv(args.data, parse_dates=True, index_col=0)

    filters_df = pd.read_csv(args.filters)

    if args.cmd == "scan-day":
        rows = run_scan_day(df, args.date, filters_df, alias_csv=args.alias)
        if not flags.write_outputs:
            print("ℹ️ CL003: --no-write aktif; dosya yazımı yok. Sinyal adedi:", len(rows))
            sys.exit(0)
        from backtest.batch.io import OutputWriter
        out = OutputWriter(cfg["paths"]["outputs"] if not args.out else args.out)
        out.write_day(args.date, rows)
        sys.exit(0)

    if args.cmd == "scan-range":
        if not flags.filters_enabled:
            logger.warning("filters_enabled=false → sadece veri/indikatör hazırlığı yapılır")
        run_scan_range(
            df, args.start, args.end, filters_df,
            out_dir=(cfg["paths"]["outputs"] if not args.out else args.out),
            alias_csv=args.alias,
        )
        if not flags.write_outputs:
            print("ℹ️ CL003: --no-write aktif; dosya yazımı yok (bilgi).")
        sys.exit(0)


if __name__ == "__main__":
    main()
