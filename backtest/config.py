from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Literal

import yaml
from pydantic import BaseModel, Field
import warnings
from loguru import logger

from utils.paths import resolve_path
from .paths import resolve_under_root


class ProjectCfg(BaseModel):
    out_dir: str = "raporlar"
    run_mode: str = "range"  # range | single
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    single_date: Optional[str] = None
    holding_period: int = 1
    transaction_cost: float = 0.0
    raise_on_error: bool = False
    stop_on_filter_error: bool = False


class DataCfg(BaseModel):
    excel_dir: str
    filters_csv: str = "filters.csv"
    enable_cache: bool = False
    cache_parquet_path: Optional[str] = None
    corporate_actions_csv: Optional[str] = None
    filename_pattern: str = "{date}.xlsx"
    date_format: str = "%Y-%m-%d"
    case_sensitive: bool = True
    suggestions: bool = True
    price_schema: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "date": ["Tarih", "Date", "tarih"],
            "open": ["Açılış", "Acılıs", "Open", "Acilis"],
            "high": ["Yüksek", "Yuksek", "High"],
            "low": ["Düşük", "Dusuk", "Low"],
            "close": ["Kapanış", "Close"],
            "volume": ["Hacim", "Volume", "Adet"],
        }
    )


class CalendarCfg(BaseModel):
    tplus1_mode: str = "price"  # price | calendar
    holidays_source: str = "none"  # none | csv
    holidays_csv_path: Optional[str] = None


class IndicatorsCfg(BaseModel):
    engine: Literal["none"] = "none"
    params: Dict[str, List[int]] = Field(
        default_factory=lambda: {"rsi": [14], "ema": [10, 20, 50], "macd": [12, 26, 9]}
    )


class BenchmarkCfg(BaseModel):
    source: str = "none"  # none | excel | csv
    excel_path: str = ""
    excel_sheet: str = "BIST"
    csv_path: str = ""
    column_date: str = "date"
    column_close: str = "close"


class ReportCfg(BaseModel):
    percent_format: str = "0.00%"
    daily_sheet_prefix: str = "SCAN_"
    summary_sheet_name: str = "SUMMARY"
    with_bist_ratio_summary: bool = False


class RootCfg(BaseModel):
    preflight: bool = True
    project: ProjectCfg
    data: DataCfg
    calendar: CalendarCfg = Field(default_factory=CalendarCfg)
    indicators: IndicatorsCfg = Field(default_factory=IndicatorsCfg)
    benchmark: BenchmarkCfg = Field(default_factory=BenchmarkCfg)
    report: ReportCfg = Field(default_factory=ReportCfg)


def load_config(path: str | Path) -> RootCfg:
    p = resolve_path(path)
    if not p.exists():
        msg = (
            f"Config bulunamadı: {p}. "
            "'--config' ile yol belirtin veya config şablonunu kontrol edin."
        )
        logger.error(msg)
        raise FileNotFoundError(msg)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise TypeError("Config içeriği sözlük olmalı")
    data_section = cfg.get("data", {})
    if "excel_dir" in data_section:
        data_section["excel_dir"] = str(
            resolve_under_root(p, data_section["excel_dir"])
        )
    if "filters_csv" in data_section:
        data_section["filters_csv"] = str(
            resolve_under_root(p, data_section["filters_csv"])
        )
    cfg["data"] = data_section
    base = p.parent

    def _join(v: Optional[str], *, allow_cwd: bool = False) -> Optional[str]:
        if not v:
            return v
        raw = os.path.expandvars(v)
        vp = Path(raw).expanduser()
        if not vp.is_absolute():
            candidate = (base / vp).resolve()
            if allow_cwd and not candidate.exists():
                cwd_candidate = (Path.cwd() / vp).resolve()
                if cwd_candidate.exists():
                    candidate = cwd_candidate
            vp = candidate
        else:
            vp = vp.resolve()
        return str(vp)

    proj = cfg.get("project", {}) if isinstance(cfg, dict) else {}
    if isinstance(proj, dict) and proj.get("out_dir"):
        proj["out_dir"] = _join(proj.get("out_dir"))
    data = cfg.get("data", {}) if isinstance(cfg, dict) else {}
    for req_key in ("excel_dir",):
        if not data.get(req_key):
            raise ValueError(
                f"config.data.{req_key} zorunlu; "
                "örnek için examples/example_config.yaml"
            )
    for k in [
        "excel_dir",
        "filters_csv",
        "cache_parquet_path",
        "corporate_actions_csv",
    ]:
        v = data.get(k)
        if v:
            data[k] = _join(v, allow_cwd=(k == "filters_csv"))
    cal = cfg.get("calendar", {}) if isinstance(cfg, dict) else {}
    if isinstance(cal, dict) and cal.get("holidays_csv_path"):
        cal["holidays_csv_path"] = _join(cal.get("holidays_csv_path"))
    bench = cfg.get("benchmark", {}) if isinstance(cfg, dict) else {}
    if isinstance(bench, dict):
        if "xu100_source" in bench and "source" not in bench:
            warnings.warn(
                "benchmark.xu100_source deprecated; use benchmark.source",
                DeprecationWarning,
            )
            bench["source"] = bench.pop("xu100_source")
        if "xu100_csv_path" in bench and "csv_path" not in bench:
            warnings.warn(
                "benchmark.xu100_csv_path deprecated; use benchmark.csv_path",
                DeprecationWarning,
            )
            bench["csv_path"] = bench.pop("xu100_csv_path")
        for k in ("excel_path", "csv_path"):
            if bench.get(k):
                bench[k] = str(resolve_under_root(p, bench[k]))
    indicators = cfg.get("indicators", {}) if isinstance(cfg, dict) else {}
    eng = indicators.get("engine")
    if eng is not None and eng != "none":
        raise ValueError(
            "indicators.engine politika gereği devre dışı (engine='none')."
        )
    indicators["engine"] = "none"
    (
        cfg["project"],
        cfg["data"],
        cfg["calendar"],
        cfg["benchmark"],
        cfg["indicators"],
    ) = (
        proj,
        data,
        cal,
        bench,
        indicators,
    )
    return RootCfg(**cfg)
