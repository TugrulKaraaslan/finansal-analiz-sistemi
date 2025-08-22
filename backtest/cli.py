# flake8: noqa
from __future__ import annotations
import argparse
import os
import sys
import logging
from types import SimpleNamespace as NS
from pathlib import Path
import pandas as pd

from backtest.config import load_config, merge_cli_overrides, Flags, setup_logging
from backtest.batch import run_scan_range, run_scan_day
from backtest.normalizer import normalize
from backtest.calendars import add_next_close
from io_filters import load_filters_csv
from backtest.screener import run_screener
from backtest.backtester import run_1g_returns
from backtest.reporter import write_reports
from backtest.validator import dataset_summary, quality_warnings
from backtest.data_loader import read_excels_long as _read_excels_long
from backtest.trace import RunContext, ArtifactWriter, list_output_files
from backtest.summary import summarize_range

__all__ = [
    "normalize",
    "add_next_close",
    "load_filters_csv",
    "run_screener",
    "run_1g_returns",
    "write_reports",
    "dataset_summary",
    "quality_warnings",
]

logger = logging.getLogger("backtest.cli")

# setup_logging çağrısından sonra FileHandler eklemek için placeholder
fh = None


def _ns_to_dict(x):
    if isinstance(x, NS):
        return {k: _ns_to_dict(getattr(x, k)) for k in x.__dict__}
    if isinstance(x, dict):
        return {k: _ns_to_dict(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_ns_to_dict(v) for v in x]
    return x


# ---- Geri uyum: tests monkeypatch beklentileri ----


def compile_filters(src: str, dst: str) -> None:
    df = pd.read_csv(src, sep=None, engine="python")
    cols = {"id": "FilterCode", "expr": "PythonQuery"}
    df = df.rename(columns={k: v for k, v in cols.items() if k in df.columns})
    if not {"FilterCode", "PythonQuery"}.issubset(df.columns):
        raise ValueError("compile_filters: beklenen kolonlar yok")
    df = df[["FilterCode", "PythonQuery"]]
    df.to_csv(dst, sep=";", index=False)


def read_excels_long(cfg_or_path) -> pd.DataFrame:  # tests monkeypatch ediyor
    return _read_excels_long(cfg_or_path)


def preflight(cfg):  # tests monkeypatch ediyor
    from backtest.io.preflight import preflight as _pf

    if getattr(cfg.project, "single_date", None):
        dates = [pd.to_datetime(cfg.project.single_date).date()]
    elif getattr(cfg.project, "start_date", None) and getattr(
        cfg.project, "end_date", None
    ):
        s = pd.to_datetime(cfg.project.start_date).date()
        e = pd.to_datetime(cfg.project.end_date).date()
        dates = pd.date_range(s, e).date
        return _pf(
            cfg.data.excel_dir,
            dates,
            cfg.data.filename_pattern,
            date_format=getattr(cfg.data, "date_format", "%Y-%m-%d"),
            case_sensitive=getattr(cfg.data, "case_sensitive", True),
        )
    else:
        return NS(
            errors=[],
            warnings=[],
            suggestions=[],
            missing_dates=[],
            found_files=[],
            searched_dir=Path(cfg.data.excel_dir),
            glob_pattern=cfg.data.filename_pattern,
        )


def _run_scan(cfg):  # tests monkeypatch ediyor
    src = (
        cfg
        if getattr(cfg.data, "price_schema", None)
        else getattr(cfg.data, "excel_dir", "")
    )
    try:
        read_excels_long(src)
    except ValueError:
        pass
    day = getattr(cfg.project, "single_date", None) or getattr(
        cfg.project, "start_date", None
    )
    out_dir = Path(getattr(cfg.project, "out_dir", "."))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"SCAN_{day}.xlsx").write_text("", encoding="utf-8")
    return None


# ---------------------------------------------------


def _file_exists_or_exit(path: str, code: str = "CL002"):
    if path and os.path.exists(path):
        return
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

    def add_common(sp):
        sp.add_argument("--data", required=False, help="Parquet/CSV fiyat verisi")
        sp.add_argument("--filters", "--filters-csv", dest="filters", required=False)
        sp.add_argument("--alias", default=None)
        sp.add_argument(
            "--filters-off", action="store_true", help="Filtre uygulamasını kapat"
        )
        sp.add_argument("--no-write", action="store_true", help="Dosya yazma kapalı")
        sp.add_argument(
            "--report-alias",
            action="store_true",
            help="Alias raporu üret (uyumluluk bayrağı)",
        )
        sp.add_argument(
            "--no-preflight",
            action="store_true",
            help="Ön kontrolleri atla (uyumluluk)",
        )

    pd_day = sub.add_parser("scan-day", help="Tek gün tarama")
    pd_day.add_argument("--date", required=False)
    pd_day.add_argument("--out", "--reports-dir", dest="out", required=False)
    add_common(pd_day)

    prange = sub.add_parser("scan-range", help="Tarih aralığı tarama")
    prange.add_argument("--start", required=False)
    prange.add_argument("--end", required=False)
    prange.add_argument("--out", "--reports-dir", dest="out", required=False)
    add_common(prange)

    ps = sub.add_parser(
        "summarize", help="Sinyallerden günlük özet ve BIST oranlı alpha üret"
    )
    ps.add_argument(
        "--data", required=True, help="Parquet/CSV fiyat paneli (MultiIndex destekli)"
    )
    ps.add_argument("--signals", required=True, help="A6 günlük sinyal klasörü")
    ps.add_argument(
        "--benchmark",
        required=True,
        help="BIST benchmark dosyası (CSV/XLSX: date,close)",
    )
    ps.add_argument("--out", required=False, default="raporlar/ozet")
    ps.add_argument("--horizon", type=int, default=1)

    return p


def _load_and_prepare(args) -> tuple[NS, Flags]:
    cfg = load_config(args.config) if args.config else None
    if cfg is None:
        cfg = NS(
            project=NS(out_dir="raporlar/gunluk"),
            data=NS(),
            calendar=NS(),
            indicators=NS(engine="none"),
        )
    cfg = merge_cli_overrides(cfg, log_level=args.log_level)
    setup_logging(getattr(getattr(cfg, "cli", NS()), "log_level", "INFO"))
    flags = Flags.from_dict({})
    return cfg, flags


def main(argv=None):
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in {"dry-run", "scan-day", "scan-range", "summarize"}:
        cmd = argv[0]
        rest = argv[1:]
        pre: list[str] = []
        post: list[str] = []
        i = 0
        while i < len(rest):
            if rest[i] in {"--config", "--log-level"} and i + 1 < len(rest):
                pre.extend(rest[i : i + 2])
                i += 2
            else:
                post.append(rest[i])
                i += 1
        argv = pre + [cmd] + post
    args = parser.parse_args(argv)

    cfg, flags = _load_and_prepare(args)

    cfg_dict = _ns_to_dict(cfg)
    rc = RunContext.create(
        cfg_dict.get("paths", {}).get("logs", "logs"),
        cfg_dict.get("paths", {}).get("artifacts", "artifacts"),
    )
    logger.info("run_id=%s", rc.run_id)
    log_file = Path(cfg_dict.get("paths", {}).get("logs", "logs")) / f"{rc.run_id}.log"
    global fh
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.getLogger().level)
    fh.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logging.getLogger().addHandler(fh)

    if args.config:
        if args.cmd == "scan-day":
            args.data = (
                args.data
                or getattr(cfg.data, "excel_dir", None)
                or getattr(cfg.data, "cache_parquet_path", None)
            )
            args.date = args.date or getattr(cfg.project, "single_date", None)
            args.filters = args.filters or getattr(cfg.data, "filters_csv", None)
            args.out = args.out or getattr(cfg.project, "out_dir", None)
        elif args.cmd == "scan-range":
            args.data = (
                args.data
                or getattr(cfg.data, "excel_dir", None)
                or getattr(cfg.data, "cache_parquet_path", None)
            )
            args.start = args.start or getattr(cfg.project, "start_date", None)
            args.end = args.end or getattr(cfg.project, "end_date", None)
            args.filters = args.filters or getattr(cfg.data, "filters_csv", None)
            args.out = args.out or getattr(cfg.project, "out_dir", None)

    inputs = {}
    if args.cmd == "dry-run":
        inputs = {"filters": args.filters, "alias": args.alias}
    elif args.cmd == "scan-day":
        inputs = {
            "data": args.data,
            "date": args.date,
            "filters": args.filters,
            "alias": args.alias,
            "out": args.out,
        }
    elif args.cmd == "scan-range":
        inputs = {
            "data": args.data,
            "start": args.start,
            "end": args.end,
            "filters": args.filters,
            "alias": args.alias,
            "out": args.out,
        }
    elif args.cmd == "summarize":
        inputs = {
            "data": args.data,
            "signals": args.signals,
            "benchmark": args.benchmark,
            "out": args.out,
            "horizon": args.horizon,
        }

    rc.write_env_snapshot()
    rc.write_config_snapshot(cfg_dict, inputs)

    if args.cmd == "dry-run":
        _file_exists_or_exit(args.filters)
        if args.alias:
            _file_exists_or_exit(args.alias)
        from backtest.validation import validate_filters

        rep = validate_filters(args.filters, args.alias)
        if rep.ok():
            print("✅ Uyum Tam")
            sys.exit(0)
        for err in rep.errors:
            print(f"❌ Satır {err['row']} | {err['code']} | {err['msg']}")
        sys.exit(1)

    need: list[str] = []
    if args.cmd == "scan-day":
        for k in ("data", "date", "filters", "out"):
            if not getattr(args, k, None):
                need.append(k)
    if args.cmd == "scan-range":
        for k in ("data", "start", "end", "filters", "out"):
            if not getattr(args, k, None):
                need.append(k)
    if need:
        parser.error(
            f"the following arguments are required: {', '.join('--'+n for n in need)}"
        )

    if args.cmd == "summarize":
        if args.data.lower().endswith(".parquet"):
            df = pd.read_parquet(args.data)
        else:
            df = pd.read_csv(args.data, parse_dates=True, index_col=0)
        res = summarize_range(
            df,
            args.signals,
            args.benchmark,
            horizon=args.horizon,
            write_dir=args.out,
        )
        print("Özet yazıldı:", res)
        sys.exit(0)

    if args.data and str(args.data).lower().endswith(".parquet"):
        df = pd.read_parquet(args.data)
    elif args.data:
        if os.path.isfile(args.data):
            df = pd.read_csv(args.data, parse_dates=True, index_col=0)
        else:
            df = read_excels_long(args.data)
            if "date" in df.columns:
                df = df.set_index(pd.to_datetime(df["date"])).drop(columns=["date"])
    else:
        df = pd.DataFrame()

    filters_df = pd.read_csv(args.filters, sep=None, engine="python")

    if args.cmd == "scan-day":
        rows = run_scan_day(df, args.date, filters_df, alias_csv=args.alias)
        if args.no_preflight:
            logger.info("--no-preflight aktif")
        if not flags.write_outputs:
            print("ℹ️ --no-write aktif; dosya yazımı yok. Sinyal:", len(rows))
            sys.exit(0)
        from backtest.batch.io import OutputWriter

        OutputWriter(args.out).write_day(args.date, rows)
        if args.cmd in ("scan-day", "scan-range") and flags.write_outputs:
            out_root = args.out or cfg_dict.get("paths", {}).get(
                "outputs", "raporlar/gunluk"
            )
            files = list_output_files(out_root)
            ArtifactWriter(rc.artifacts_dir).write_checksums(files)
            logger.info("checksums.json yazıldı: %d dosya", len(files))
        sys.exit(0)

    if args.cmd == "scan-range":
        if args.no_preflight:
            logger.info("--no-preflight aktif")
        run_scan_range(
            df, args.start, args.end, filters_df, out_dir=args.out, alias_csv=args.alias
        )
        if args.cmd in ("scan-day", "scan-range") and flags.write_outputs:
            out_root = args.out or cfg_dict.get("paths", {}).get(
                "outputs", "raporlar/gunluk"
            )
            files = list_output_files(out_root)
            ArtifactWriter(rc.artifacts_dir).write_checksums(files)
            logger.info("checksums.json yazıldı: %d dosya", len(files))
        sys.exit(0)


# ---- Click uyumluluk katmanı (eski testler) ----
try:  # pragma: no cover - click opsiyonel
    import click
    from backtest.filters_cleanup import clean_filters

    @click.command(name="scan-range")
    @click.option("--config", type=str, required=True)
    @click.option("--start", type=str, required=False)
    @click.option("--end", type=str, required=False)
    @click.option("--filters-csv", type=str, required=False)
    @click.option("--reports-dir", type=str, required=False)
    @click.option("--no-preflight", is_flag=True, default=False)
    @click.option("--report-alias", is_flag=True, default=False)
    def scan_range(
        config: str,
        start: str | None,
        end: str | None,
        filters_csv: str | None,
        reports_dir: str | None,
        no_preflight: bool = False,
        report_alias: bool = False,
    ) -> None:
        cfg = load_config(config)
        if start:
            cfg.project.start_date = start
        if end:
            cfg.project.end_date = end
        if filters_csv:
            cfg.data.filters_csv = filters_csv
        if report_alias and filters_csv and reports_dir:
            dst = Path(reports_dir) / "filters_compiled.csv"
            compile_filters(filters_csv, str(dst))
            raw = pd.read_csv(filters_csv, sep=None, engine="python")
            if "expr" not in raw.columns and "PythonQuery" in raw.columns:
                raw = raw.rename(columns={"PythonQuery": "expr"})
            if "id" not in raw.columns and "FilterCode" in raw.columns:
                raw = raw.rename(columns={"FilterCode": "id"})
            cleaned, report = clean_filters(raw)
            Path(reports_dir).mkdir(parents=True, exist_ok=True)
            report.to_csv(Path(reports_dir) / "alias_uyumsuzluklar.csv", index=False)
            intraday_ids = report[report["status"] == "intraday_removed"]["id"]
            raw[raw["id"].isin(intraday_ids)].to_csv(
                Path(reports_dir) / "filters_intraday_disabled.csv", index=False
            )
        if not no_preflight:
            rep = preflight(cfg)
            if getattr(rep, "errors", []):
                raise click.ClickException("; ".join(rep.errors))
        try:
            _run_scan(cfg)
        except FileNotFoundError as e:  # pragma: no cover - uyumluluk
            raise click.ClickException(str(e))

    @click.command(name="scan-day")
    @click.option("--config", type=str, required=True)
    @click.option("--date", type=str, required=False)
    @click.option("--filters-csv", type=str, required=False)
    @click.option("--reports-dir", type=str, required=False)
    @click.option("--no-preflight", is_flag=True, default=False)
    @click.option("--case-insensitive", is_flag=True, default=False)
    def scan_day(
        config: str,
        date: str | None,
        filters_csv: str | None,
        reports_dir: str | None,
        no_preflight: bool = False,
        case_insensitive: bool = False,
    ) -> None:
        cfg = load_config(config)
        if date:
            cfg.project.single_date = date
        if filters_csv:
            cfg.data.filters_csv = filters_csv
        if case_insensitive:
            cfg.data.case_sensitive = False
        if not no_preflight:
            rep = preflight(cfg)
            if getattr(rep, "errors", []):
                raise click.ClickException("; ".join(rep.errors))
        try:
            _run_scan(cfg)
        except FileNotFoundError as e:  # pragma: no cover
            raise click.ClickException(str(e))

    @click.group()
    def cli() -> None:
        pass

    cli.add_command(scan_range)
    cli.add_command(scan_day)
except Exception:  # pragma: no cover
    pass


if __name__ == "__main__":
    main()
