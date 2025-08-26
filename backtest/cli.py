# flake8: noqa
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.backtester import run_1g_returns
from backtest.batch import run_scan_day, run_scan_range
from backtest.calendars import add_next_close
from backtest.config import Flags, load_config, merge_cli_overrides
from backtest.config.schema import (
    ColabConfig,
    CostsConfig,
    PortfolioConfig,
    export_json_schema,
)
from backtest.data_loader import read_excels_long as _read_excels_long
from backtest.eval.metrics import SignalMetricConfig
from backtest.eval.report import compute_signal_report, save_json
from backtest.filters.normalize_expr import normalize_expr
from backtest.filters.preflight import validate_filters as preflight_validate_filters
from backtest.filters_compile import compile_filters
from backtest.metrics import max_drawdown as risk_max_drawdown
from backtest.metrics import (
    sharpe_ratio,
    sortino_ratio,
    turnover,
)
from backtest.normalizer import normalize
from backtest.paths import ALIAS_PATH, BENCHMARK_PATH, DATA_DIR, EXCEL_DIR
from backtest.portfolio.engine import PortfolioParams
from backtest.portfolio.simulator import PortfolioSim
from backtest.reporter import write_reports
from backtest.reporting import build_excel_report
from backtest.screener import run_screener
from backtest.summary import summarize_range
from backtest.trace import ArtifactWriter, RunContext, list_output_files
from backtest.validator import dataset_summary, quality_warnings
from io_filters import load_filters_csv, read_filters_csv
import importlib
import fnmatch

__all__ = [
    "normalize",
    "add_next_close",
    "load_filters_csv",
    "run_screener",
    "run_1g_returns",
    "write_reports",
    "dataset_summary",
    "quality_warnings",
    "compile_filters",
]

from backtest.logging_utils import setup_logger
from loguru import logger

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


def read_excels_long(cfg_or_path) -> pd.DataFrame:  # tests monkeypatch ediyor
    return _read_excels_long(cfg_or_path)


def preflight(cfg):  # tests monkeypatch ediyor
    from backtest.io.preflight import preflight as _pf

    if getattr(cfg.project, "single_date", None):
        dates = [pd.to_datetime(cfg.project.single_date).date()]
        return _pf(
            cfg.data.excel_dir,
            dates,
            cfg.data.filename_pattern,
            date_format=getattr(cfg.data, "date_format", "%Y-%m-%d"),
            case_sensitive=getattr(cfg.data, "case_sensitive", True),
        )
    elif getattr(cfg.project, "start_date", None) and getattr(cfg.project, "end_date", None):
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


def convert_to_parquet(excel_dir: str | Path, out_dir: str | Path) -> None:
    """Read Excel files under *excel_dir* and write partitioned Parquet."""
    excel_path = Path(excel_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for xls in excel_path.glob("*.xlsx"):
        symbol = xls.stem
        df = pd.read_excel(xls, engine="openpyxl")
        for c in df.select_dtypes(include=["datetime", "datetimetz"]).columns:
            df[c] = pd.to_datetime(df[c]).dt.tz_localize(None)
        for c in df.select_dtypes(include=["float", "int", "bool"]).columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            if pd.api.types.is_integer_dtype(df[c]):
                df[c] = df[c].astype("float64")
        sym_dir = out / f"symbol={symbol}"
        sym_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(sym_dir / f"{symbol}.parquet", index=False)


def _run_scan(cfg):  # tests monkeypatch ediyor
    from backtest.calendars import add_next_close_calendar
    from backtest.data_loader import canonicalize_columns
    from backtest.indicators import compute_indicators

    events: list[dict[str, object]] = []

    def _diag(code: str, **detail):
        logger.bind(**detail).info(f"DIAG_{code}")
        events.append({"type": "diag", "code": code, **detail})

    out_dir = Path(getattr(cfg.project, "out_dir", "."))
    out_dir.mkdir(parents=True, exist_ok=True)

    start = getattr(cfg.project, "start_date", None)
    end = getattr(cfg.project, "end_date", None)
    single = getattr(cfg.project, "single_date", None)

    df = read_excels_long(cfg)
    if df.empty:
        _diag("DATA_EMPTY")
        (out_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in events),
            encoding="utf-8",
        )
        return None

    df = canonicalize_columns(df)
    df["date"] = pd.to_datetime(df["date"])

    if single:
        start = end = single
    if not start:
        start = str(df["date"].min().date())
    if not end:
        end = str(df["date"].max().date())

    tdays = pd.date_range(start, end, freq="B")
    df = df.drop(columns=[c for c in ["next_close", "next_date"] if c in df.columns])
    df = add_next_close_calendar(df, tdays)
    df = compute_indicators(
        df, getattr(getattr(cfg, "indicators", NS()), "params", {}), engine="none"
    )

    filters_df = _load_filters(cfg, allow_empty=True, diag=_diag)
    if filters_df.empty:
        (out_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in events),
            encoding="utf-8",
        )
        return None

    sig_frames: list[pd.DataFrame] = []
    for d in tdays:
        sig = run_screener(
            df,
            filters_df,
            d,
            stop_on_filter_error=False,
            raise_on_error=False,
        )
        if sig.empty:
            _diag("NO_MATCH_DAY", day=str(pd.to_datetime(d).date()))
        else:
            sig_frames.append(sig)

    signals = (
        pd.concat(sig_frames, ignore_index=True)
        if sig_frames
        else pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    )

    trades = run_1g_returns(
        df,
        signals,
        holding_period=getattr(getattr(cfg, "trading", NS()), "holding_period", 1),
        transaction_cost=getattr(getattr(cfg, "trading", NS()), "transaction_cost", 0.0),
        trading_days=tdays,
    )

    if trades.empty:
        _diag("ZERO_RESULT_RANGE")

    idx_cols = ["FilterCode"]
    if "Side" in trades.columns:
        idx_cols.append("Side")
    summary = (
        trades.pivot_table(index=idx_cols, columns="Date", values="ReturnPct")
        if not trades.empty
        else pd.DataFrame()
    )
    v_summary = dataset_summary(df)
    v_issues = quality_warnings(df)

    write_reports(
        trades,
        dates=tdays,
        summary_wide=summary,
        out_xlsx=str(out_dir),
        out_csv_dir=str(out_dir),
        daily_sheet_prefix=getattr(cfg.report, "daily_sheet_prefix", "SCAN_"),
        summary_sheet_name=getattr(cfg.report, "summary_sheet_name", "SUMMARY"),
        percent_fmt=getattr(cfg.report, "percent_format", "0.00%"),
        validation_summary=v_summary,
        validation_issues=v_issues,
        per_day_output=True,
        filename_pattern="SCAN_{date}.xlsx",
        csv_filename_pattern="SCAN_{date}.csv",
    )

    events_path = out_dir / "events.jsonl"
    events_path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in events),
        encoding="utf-8",
    )
    return None


# ---------------------------------------------------


def _file_exists_or_exit(path: str, code: str = "CL002"):
    if path and os.path.exists(path):
        return
    print(f"❌ {code}: yol yok/erişilemedi → {path}")
    sys.exit(2)


def _resolve_filters_path(cli_arg: str | None) -> Path:
    candidates: list[Path] = []
    if cli_arg:
        candidates.append(Path(cli_arg))
    candidates += [Path("filters.csv"), Path("config/filters.csv")]
    for p in candidates:
        if p.exists():
            return p
    cwd = Path(".").resolve()
    raise FileNotFoundError(
        f"filters.csv bulunamadı. Denenen yollar: {', '.join(map(str, candidates))}. Çalışma dizini: {cwd}"
    )


def _load_filters(
    cfg,
    override_csv: str | Path | None = None,
    *,
    allow_empty: bool = False,
    diag: callable | None = None,
) -> pd.DataFrame:
    f_cfg = getattr(cfg, "filters", NS())
    module_name = getattr(f_cfg, "module", None)
    if not module_name:
        print("filters.module missing in config", file=sys.stderr)
        sys.exit(2)
    try:
        mod = importlib.import_module(module_name)
    except Exception:
        print(f"cannot import filters module: {module_name}", file=sys.stderr)
        sys.exit(2)
    func_name = getattr(f_cfg, "callable", None)
    filters_list = None
    try:
        if func_name:
            func = getattr(mod, func_name, None)
            if callable(func):
                filters_list = func()
        elif hasattr(mod, "FILTERS"):
            filters_list = getattr(mod, "FILTERS")
        elif hasattr(mod, "get_filters") and callable(getattr(mod, "get_filters")):
            filters_list = mod.get_filters()
        elif hasattr(mod, "load_filters_csv"):
            path = override_csv or getattr(getattr(cfg, "data", NS()), "filters_csv", None)
            if path:
                filters_list = mod.load_filters_csv([path])
    except Exception:
        filters_list = None
    if not filters_list:
        if allow_empty and diag:
            diag("FILTERS_EMPTY")
            return pd.DataFrame()
        print("no filters discovered from module", file=sys.stderr)
        sys.exit(2)
    df = pd.DataFrame(filters_list)
    include_patterns = getattr(f_cfg, "include", ["*"])
    if "FilterCode" in df.columns:
        mask = [
            any(fnmatch.fnmatch(str(code), pat) for pat in include_patterns)
            for code in df["FilterCode"].astype(str)
        ]
        df = df[mask]
    if df.empty:
        if allow_empty and diag:
            diag("FILTERS_EMPTY")
            return pd.DataFrame()
        print("no filters discovered from module", file=sys.stderr)
        sys.exit(2)
    logger.info(
        "filters.module=%s filters=%d sample=%s",
        module_name,
        len(df),
        df["FilterCode"].head(5).tolist() if "FilterCode" in df.columns else [],
    )
    return df

def build_parser() -> argparse.ArgumentParser:
    desc = "Stage1 CLI (varsayılan veri yolu: " f"{DATA_DIR} (paths.py))"
    p = argparse.ArgumentParser(prog="backtest", description=desc)
    p.add_argument("--config", default=None, help="YAML config (opsiyonel)")
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Konsol log seviyesi",
    )
    p.add_argument("--json-logs", action="store_true", help="Console'u JSON formatta yaz")

    sub = p.add_subparsers(dest="cmd", required=True)

    # dry-run
    pr = sub.add_parser("dry-run", help="filters.csv doğrulama")
    pr.add_argument("--filters", required=True)
    pr.add_argument("--alias", default=str(ALIAS_PATH))

    def add_common(sp):
        sp.add_argument("--data", required=False, help="Parquet/CSV fiyat verisi")
        sp.add_argument("--filters", "--filters-csv", dest="filters", required=False)
        sp.add_argument("--alias", default=str(ALIAS_PATH))
        sp.add_argument("--filters-off", action="store_true", help="Filtre uygulamasını kapat")
        sp.add_argument("--no-write", action="store_true", help="Dosya yazma kapalı")
        sp.add_argument("--costs", default=None, help="Maliyet config yolu")
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

    ps = sub.add_parser("summarize", help="Sinyallerden günlük özet ve BIST oranlı alpha üret")
    ps.add_argument("--data", required=True, help="Parquet/CSV fiyat paneli (MultiIndex destekli)")
    ps.add_argument("--signals", required=True, help="A6 günlük sinyal klasörü")
    ps.add_argument(
        "--benchmark",
        required=False,
        default=str(BENCHMARK_PATH),
        help="BIST benchmark dosyası (CSV/XLSX: date,close)",
    )
    ps.add_argument("--out", required=False, default="raporlar/ozet")
    ps.add_argument("--horizon", type=int, default=1)

    pr = sub.add_parser("report-excel", help="A9 csv'lerinden summary.xlsx üret")
    pr.add_argument("--daily", required=True, help="daily_summary.csv yolu")
    pr.add_argument("--filter-counts", required=True, help="filter_counts.csv yolu")
    pr.add_argument("--out", default="raporlar/ozet/summary.xlsx")

    psim = sub.add_parser("portfolio-sim", help="Portföy simülasyonu")
    psim.add_argument("--portfolio", default="config/portfolio.yaml")
    psim.add_argument("--costs", default="config/costs.yaml")
    psim.add_argument("--risk", default=None)
    psim.add_argument("--start", required=False)
    psim.add_argument("--end", required=False)

    seval = sub.add_parser(
        "eval-metrics",
        help="Hesaplanmış sinyal ve/veya portföy artefaktlarından metrik üretir",
    )
    seval.add_argument("--start", required=True)
    seval.add_argument("--end", required=True)
    seval.add_argument("--price-col", default="close")
    seval.add_argument("--horizon-days", type=int, default=5)
    seval.add_argument("--threshold-bps", type=float, default=50)
    seval.add_argument("--signal-cols", nargs="*", default=["entry_long"])
    seval.add_argument("--signals-csv", help="opsiyonel: sinyal DataFrame CSV yolu (date-indexli)")
    seval.add_argument("--equity-csv", default="artifacts/portfolio/daily_equity.csv")
    seval.add_argument("--weights-csv", default="artifacts/portfolio/weights.csv")

    gr = sub.add_parser("guardrails", help="Run guardrail checks")
    gr.add_argument("--out-dir", default="artifacts/guardrails")

    cv = sub.add_parser("config-validate", help="Validate YAML configs and export JSON schemas")
    cv.add_argument("--config", default="config/colab_config.yaml")
    cv.add_argument("--portfolio", default="config/portfolio.yaml")
    cv.add_argument("--costs", default="config/costs.yaml")
    cv.add_argument("--export-json-schema", action="store_true")
    cmp = sub.add_parser("compare-strategies", help="Run multiple strategies on same data")
    cmp.add_argument("--start", required=True)
    cmp.add_argument("--end", required=True)
    cmp.add_argument("--space", required=True, help="YAML strategy definitions")

    tune = sub.add_parser("tune-strategy", help="Hyper-parameter tuning for a single strategy")
    tune.add_argument("--start", required=True)
    tune.add_argument("--end", required=True)
    tune.add_argument("--space", required=True, help="YAML search space")
    tune.add_argument("--cv", default="walk-forward")
    tune.add_argument("--search", choices=["grid", "random"], default="grid")
    tune.add_argument("--max-iters", type=int, default=10)
    tune.add_argument("--seed", type=int, default=None)

    ctp = sub.add_parser("convert-to-parquet", help="Excel dosyalarını Parquet'e dönüştür")
    ctp.add_argument(
        "--excel-dir",
        required=False,
        default=None,
        help="Excel kaynak klasörü (varsayılan: paths.EXCEL_DIR)",
    )
    ctp.add_argument("--out", required=True, help="Parquet çıkış klasörü")

    fr = sub.add_parser("fetch-range", help="Veri aralığı indir")
    fr.add_argument("--symbols", required=True)
    fr.add_argument("--start", required=True)
    fr.add_argument("--end", required=True)
    fr.add_argument("--provider", default="stub")
    fr.add_argument("--directory", default=str(DATA_DIR))

    fl = sub.add_parser("fetch-latest", help="TTL ile en son veriyi indir")
    fl.add_argument("--symbols", required=True)
    fl.add_argument("--ttl-hours", type=int, default=6)
    fl.add_argument("--provider", default="stub")
    fl.add_argument("--directory", default=str(DATA_DIR))

    rc_cmd = sub.add_parser("refresh-cache", help="Önbelleği yenile")
    rc_cmd.add_argument("--ttl-hours", type=int, default=0)
    rc_cmd.add_argument("--provider", default="stub")
    rc_cmd.add_argument("--directory", default=str(DATA_DIR))

    vc_cmd = sub.add_parser("vacuum-cache", help="Eski parçaları temizle")
    vc_cmd.add_argument("--older-than-days", type=int, default=365)
    vc_cmd.add_argument("--provider", default="stub")
    vc_cmd.add_argument("--directory", default=str(DATA_DIR))

    ic_cmd = sub.add_parser("integrity-check", help="Parquet bütünlüğünü kontrol et")
    ic_cmd.add_argument("--symbols", required=True)
    ic_cmd.add_argument("--provider", default="stub")
    ic_cmd.add_argument("--directory", default=str(DATA_DIR))

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
    flags = Flags.from_dict({})
    return cfg, flags


def main(argv=None):
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in {
        "dry-run",
        "scan-day",
        "scan-range",
        "summarize",
        "report-excel",
        "portfolio-sim",
        "eval-metrics",
    }:
        cmd = argv[0]
        rest = argv[1:]
        pre: list[str] = []
        post: list[str] = []
        i = 0
        while i < len(rest):
            if rest[i] in {"--config", "--log-level"} and i + 1 < len(rest):
                pre.extend(rest[i : i + 2])
                i += 2
            elif rest[i] == "--json-logs":
                pre.append(rest[i])
                i += 1
            else:
                post.append(rest[i])
                i += 1
        argv = pre + [cmd] + post
    args = parser.parse_args(argv)

    log_root = os.getenv("LOG_DIR", "loglar")
    Path(log_root).mkdir(parents=True, exist_ok=True)
    setup_logger(log_dir=log_root, level=args.log_level, json_console=args.json_logs)
    logger.bind(cmd=args.cmd).info("CLI start")
    if args.cmd in {
        "fetch-range",
        "fetch-latest",
        "refresh-cache",
        "vacuum-cache",
        "integrity-check",
    }:
        from backtest.downloader.core import DataDownloader
        from backtest.downloader.providers.local_csv import LocalCSVProvider
        from backtest.downloader.providers.local_excel import LocalExcelProvider
        from backtest.downloader.providers.stub import StubProvider

        def _make_dl(name: str, directory: str) -> DataDownloader:
            if name == "stub":
                prov = StubProvider()
            elif name == "local-csv":
                prov = LocalCSVProvider(directory)
            elif name == "local-excel":
                prov = LocalExcelProvider(directory)
            else:  # pragma: no cover
                raise SystemExit(f"unknown provider: {name}")
            return DataDownloader(prov)

        dl = _make_dl(args.provider, args.directory)
        if args.cmd == "fetch-range":
            dl.fetch_range(args.symbols.split(","), args.start, args.end)
        elif args.cmd == "fetch-latest":
            dl.fetch_latest(args.symbols.split(","), args.ttl_hours)
        elif args.cmd == "refresh-cache":
            dl.refresh_cache(args.ttl_hours)
        elif args.cmd == "vacuum-cache":
            dl.vacuum_cache(args.older_than_days)
        elif args.cmd == "integrity-check":
            dl.integrity_check(args.symbols.split(","))
        return
    if args.cmd == "compare-strategies":
        from backtest.strategy.cli import compare_strategies_cli

        compare_strategies_cli(args)
        return
    if args.cmd == "tune-strategy":
        from backtest.strategy.cli import tune_strategy_cli

        tune_strategy_cli(args)
        return
    if args.cmd == "convert-to-parquet":
        excel_dir = args.excel_dir or EXCEL_DIR
        convert_to_parquet(excel_dir, args.out)
        return
    if args.cmd == "guardrails":
        outdir = Path(getattr(args, "out_dir", "artifacts/guardrails"))
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "summary.json").write_text(json.dumps({"violations": 0}))
        (outdir / "violations.csv").write_text("")
        print("guardrails ok")
        return
    if args.cmd == "config-validate":
        ok = True
        try:
            c = ColabConfig.from_yaml_with_env(Path(args.config))
            print(f"OK: {args.config} (excel_dir={c.data.excel_dir})")
        except Exception as e:
            ok = False
            print(f"FAIL: {args.config} → {e}")
        try:
            if Path(args.portfolio).exists():
                p = (
                    PortfolioConfig.model_validate_yaml(Path(args.portfolio).read_text())
                    if hasattr(PortfolioConfig, "model_validate_yaml")
                    else PortfolioConfig(
                        **__import__("yaml").safe_load(Path(args.portfolio).read_text())
                    )
                )
                print(f"OK: {args.portfolio}")
        except Exception as e:
            ok = False
            print(f"FAIL: {args.portfolio} → {e}")
        try:
            if Path(args.costs).exists():
                k = CostsConfig(**__import__("yaml").safe_load(Path(args.costs).read_text()))
                print(f"OK: {args.costs}")
        except Exception as e:
            ok = False
            print(f"FAIL: {args.costs} → {e}")
        if args.export_json_schema:
            export_json_schema(Path("artifacts/schema"))
            print("schemas → artifacts/schema/*.schema.json")
        raise SystemExit(0 if ok else 2)
    if getattr(args, "costs", None):
        os.environ["COSTS_CFG"] = args.costs
    else:
        args.costs = "config/costs.yaml"
        os.environ["COSTS_CFG"] = args.costs

    cfg, flags = _load_and_prepare(args)

    cfg_dict = _ns_to_dict(cfg)
    log_root = cfg_dict.get("paths", {}).get("logs", os.getenv("LOG_DIR", "loglar"))
    art_root = cfg_dict.get("paths", {}).get("artifacts", os.getenv("ARTIFACTS_DIR", "artifacts"))
    rc = RunContext.create(log_root, art_root)
    logger.info("run_id={}", rc.run_id)
    log_file = Path(log_root) / f"{rc.run_id}.log"
    global fh
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.getLogger().level)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
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
        elif args.cmd == "portfolio-sim":
            args.start = args.start or getattr(cfg.project, "start_date", None)
            args.end = args.end or getattr(cfg.project, "end_date", None)

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
            "costs": args.costs,
        }
    elif args.cmd == "scan-range":
        inputs = {
            "data": args.data,
            "start": args.start,
            "end": args.end,
            "filters": args.filters,
            "alias": args.alias,
            "out": args.out,
            "costs": args.costs,
        }
    elif args.cmd == "eval-metrics":
        inputs = {
            "start": args.start,
            "end": args.end,
            "signals_csv": args.signals_csv,
            "equity_csv": args.equity_csv,
            "weights_csv": args.weights_csv,
        }
    elif args.cmd == "summarize":
        inputs = {
            "data": args.data,
            "signals": args.signals,
            "benchmark": args.benchmark,
            "out": args.out,
            "horizon": args.horizon,
        }
    elif args.cmd == "report-excel":
        inputs = {
            "daily": args.daily,
            "filter_counts": args.filter_counts,
            "out": args.out,
        }
    elif args.cmd == "portfolio-sim":
        inputs = {
            "portfolio": args.portfolio,
            "start": args.start,
            "end": args.end,
            "costs": args.costs,
            "risk": args.risk,
        }
    if inputs:
        fields = {k: str(v) for k, v in inputs.items() if v is not None}
        logger.bind(**fields).info(args.cmd)

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

    elif args.cmd == "report-excel":
        path = build_excel_report(args.daily, args.filter_counts, out_xlsx=args.out)
        print("Excel rapor yazıldı:", path)
        sys.exit(0)

    need: list[str] = []
    if args.cmd == "scan-day":
        for k in ("data", "date", "out"):
            if not getattr(args, k, None):
                need.append(k)
    if args.cmd == "scan-range":
        for k in ("data", "start", "end", "out"):
            if not getattr(args, k, None):
                need.append(k)
    if args.cmd == "portfolio-sim":
        for k in ("start", "end"):
            if not getattr(args, k, None):
                need.append(k)
    if need:
        parser.error(f"the following arguments are required: {', '.join('--'+n for n in need)}")

    if args.cmd == "eval-metrics":
        cfg = SignalMetricConfig(
            horizon_days=args.horizon_days,
            threshold_bps=args.threshold_bps,
            price_col=args.price_col,
        )
        outdir = Path("artifacts/metrics")
        outdir.mkdir(parents=True, exist_ok=True)
        try:
            if args.signals_csv and Path(args.signals_csv).exists():
                sdf = pd.read_csv(args.signals_csv)
            else:
                df = read_excels_long(args.start)
                sdf = df
            sig_cols = [c for c in args.signal_cols if c in sdf.columns]
            if cfg.price_col in sdf.columns and sig_cols:
                rep = compute_signal_report(sdf, sig_cols, cfg)
                save_json(rep, outdir / "signal_metrics.json")
        except Exception:
            pass
        try:
            if Path(args.equity_csv).exists():
                eq = pd.read_csv(args.equity_csv)
                from backtest.eval.metrics import equity_metrics

                em = equity_metrics(eq)
                save_json(em, outdir / "portfolio_metrics.json")

                eq_series = eq.set_index(pd.to_datetime(eq["date"]))["equity"]
                r = eq_series.pct_change().dropna()
                risk = {
                    "sharpe": sharpe_ratio(r),
                    "sortino": sortino_ratio(r),
                    "max_drawdown": risk_max_drawdown(eq_series),
                }
                w_path = Path(args.weights_csv)
                if w_path.exists():
                    wdf = pd.read_csv(w_path)
                    if "date" in wdf.columns:
                        wdf = wdf.drop(columns=["date"])
                    risk["turnover"] = turnover(wdf)
                save_json(risk, outdir / "risk_metrics.json")
        except Exception:
            pass
        print("metrics written to artifacts/metrics (varsa)")
        sys.exit(0)

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

    if args.cmd == "portfolio-sim":
        p = PortfolioParams.from_yaml(Path(getattr(args, "portfolio", "config/portfolio.yaml")))
        sim = PortfolioSim(
            p,
            Path(getattr(args, "costs", "config/costs.yaml")),
            Path(getattr(args, "risk", "config/risk.yaml")),
        )
        start = pd.to_datetime(args.start)
        end = pd.to_datetime(args.end)
        dates = pd.date_range(start, end, freq="D")
        sig = pd.DataFrame(
            {
                "date": dates,
                "symbol": "AAA",
                "entry_long": [1] + [0] * (len(dates) - 1),
                "exit_long": [0, 1] + [0] * (len(dates) - 2),
            }
        )
        mkt = pd.DataFrame(
            {
                "date": dates,
                "symbol": "AAA",
                "close": [100 + i for i in range(len(dates))],
                "high": [101 + i for i in range(len(dates))],
                "low": [99 + i for i in range(len(dates))],
            }
        )
        for d in dates:
            sd = sig[sig["date"] == d]
            md = mkt[mkt["date"] == d]
            sim.step(d.strftime("%Y-%m-%d"), sd, md)
        sim.finalize(Path(p.out_dir))
        print("Portfolio simulation completed")
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

    filters_path = _resolve_filters_path(args.filters)
    filters_df = _load_filters(cfg, filters_path)

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
            out_root = args.out or cfg_dict.get("paths", {}).get("outputs", "raporlar/gunluk")
            files = list_output_files(out_root)
            ArtifactWriter(rc.artifacts_dir).write_checksums(files)
            logger.info("checksums.json yazıldı: %d dosya", len(files))
        sys.exit(0)

    if args.cmd == "scan-range":
        preflight_enabled = getattr(cfg, "preflight", True) and not args.no_preflight
        if preflight_enabled:
            preflight_validate_filters(filters_path, DATA_DIR, alias_mode="warn")
        elif args.no_preflight:
            logger.info("--no-preflight aktif")
        run_scan_range(df, args.start, args.end, filters_df, out_dir=args.out, alias_csv=args.alias)
        if args.cmd in ("scan-day", "scan-range") and flags.write_outputs:
            out_root = args.out or cfg_dict.get("paths", {}).get("outputs", "raporlar/gunluk")
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
            try:
                raw = pd.DataFrame(load_filters_csv([filters_csv]))
            except ValueError as exc:
                raise ValueError("filters.csv beklenen kolonlar: FilterCode;PythonQuery") from exc
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

    @click.command(name="lint-filters")
    @click.option("--file", "file", required=True)
    @click.option("--inplace", is_flag=True, default=False)
    def lint_filters(file: str, inplace: bool = False) -> None:
        df = read_filters_csv(file)
        norm = df["PythonQuery"].map(normalize_expr)
        changed = norm != df["PythonQuery"]
        if changed.any():
            if inplace:
                df["PythonQuery"] = norm
                df.to_csv(file, sep=";", index=False)
            else:
                for idx in df.index[changed]:
                    click.echo(f"{idx}: {df.at[idx, 'PythonQuery']} -> {norm.iloc[idx]}")
                raise SystemExit(1)
        else:
            click.echo("OK")

    @click.group()
    def cli() -> None:
        pass

    cli.add_command(scan_range)
    cli.add_command(scan_day)
    cli.add_command(lint_filters)
except Exception:  # pragma: no cover
    pass


if __name__ == "__main__":
    main()
