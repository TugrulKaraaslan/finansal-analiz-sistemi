from __future__ import annotations

import copy
import logging
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

from backtest.deprecations import emit_deprecation

try:
    import yaml
except Exception:  # pragma: no cover
    # yaml yoksa minik parser yerine hata verelim
    yaml = None

logger = logging.getLogger(__name__)

_DEFAULT = {
    "project": {
        "out_dir": "raporlar/gunluk",
        "run_mode": "range",
        "start_date": None,
        "end_date": None,
        "single_date": None,
        "holding_period": 1,
        "transaction_cost": 0.0,
        "stop_on_filter_error": False,
    },
    "data": {
        "excel_dir": "data",
        "filters_csv": "filters.csv",
        "enable_cache": False,
        "cache_parquet_path": "",
        "price_schema": {},
        "filename_pattern": "{date}.xlsx",
        "date_format": "%Y-%m-%d",
        "case_sensitive": True,
    },
    "calendar": {
        "tplus1_mode": "price",
        "holidays_source": "none",
        "holidays_csv_path": "",
    },
    "indicators": {"engine": "none", "params": {"ema": []}},
    "benchmark": {
        "source": "none",
        "excel_path": "",
        "excel_sheet": "BIST",
        "csv_path": "",
        "column_date": "date",
        "column_close": "close",
    },
    "report": {
        "percent_format": "0.00%",
        "daily_sheet_prefix": "SCAN_",
        "summary_sheet_name": "SUMMARY",
    },
    "preflight": True,
}


def _deep_merge(a: dict, b: dict) -> dict:
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _to_ns(x: Any, *, _key: str | None = None) -> Any:
    if isinstance(x, dict):
        if _key in {"params", "price_schema"}:
            return {k: _to_ns(v, _key=k) for k, v in x.items()}
        return NS(**{k: _to_ns(v, _key=k) for k, v in x.items()})
    if isinstance(x, list):
        return [_to_ns(v) for v in x]
    return x


def _apply_legacy(doc: dict) -> dict:
    bmk = doc.get("benchmark", {})
    if "xu100_source" in bmk and "source" not in bmk:
        emit_deprecation("benchmark.xu100_source", "benchmark.source")
        bmk["source"] = bmk["xu100_source"]
    if "xu100_csv_path" in bmk and "csv_path" not in bmk:
        emit_deprecation("benchmark.xu100_csv_path", "benchmark.csv_path")
        bmk["csv_path"] = bmk["xu100_csv_path"]
    doc["benchmark"] = bmk
    return doc


def _expand_paths(doc: dict, base: Path) -> dict:
    def _norm(p: str) -> str:
        if not p:
            return p
        q = Path(p)
        return str(q if q.is_absolute() else (base / q))

    if doc.get("project", {}).get("out_dir"):
        doc["project"]["out_dir"] = _norm(doc["project"]["out_dir"])
    if doc.get("data", {}).get("excel_dir"):
        doc["data"]["excel_dir"] = _norm(doc["data"]["excel_dir"])
    if doc.get("data", {}).get("filters_csv"):
        doc["data"]["filters_csv"] = _norm(doc["data"]["filters_csv"])
    if doc.get("data", {}).get("cache_parquet_path"):
        cpp = doc["data"]["cache_parquet_path"]
        doc["data"]["cache_parquet_path"] = _norm(cpp)
    if doc.get("calendar", {}).get("holidays_csv_path"):
        doc["calendar"]["holidays_csv_path"] = _norm(doc["calendar"]["holidays_csv_path"])
    for key in ("excel_path", "csv_path"):
        if doc.get("benchmark", {}).get(key):
            doc["benchmark"][key] = _norm(doc["benchmark"][key])
    return doc


def load_config(path: str | Path) -> NS:
    p = Path(path)
    if not p.exists():
        msg = f"config bulunamadı: {p.resolve()}  (İpucu: --config <dosya>)"
        logger.error(msg)
        raise FileNotFoundError(msg)
    if yaml is None:
        raise RuntimeError("PyYAML gerekli: 'pip install pyyaml'")
    with p.open("r", encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}
    if not isinstance(user, dict):
        raise TypeError("config mapping olmalı")
    user = _apply_legacy(user)
    doc = _deep_merge(_DEFAULT, user)
    if doc.get("indicators", {}).get("engine") != "none":
        raise ValueError("indicators.engine sadece 'none' olmalı")
    doc = _expand_paths(doc, p.parent)
    cfg = _to_ns(doc)
    if isinstance(cfg.indicators.params, NS):
        cfg.indicators.params = dict(cfg.indicators.params.__dict__)
    if isinstance(getattr(cfg.data, "price_schema", None), NS):
        cfg.data.price_schema = dict(cfg.data.price_schema.__dict__)
    return cfg


def merge_cli_overrides(cfg: NS, **overrides) -> NS:
    if overrides.get("log_level"):
        if not hasattr(cfg, "cli"):
            cfg.cli = NS()
        cfg.cli.log_level = overrides["log_level"]
    return cfg
