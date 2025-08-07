# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path  # TİP DÜZELTİLDİ
import warnings
import os

from pydantic import BaseModel, Field
import yaml

from utils.paths import resolve_path


class ProjectCfg(BaseModel):
    out_dir: str = "raporlar"
    run_mode: str = "range"  # range | single
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    single_date: Optional[str] = None


class DataCfg(BaseModel):
    excel_dir: str
    filters_csv: str
    enable_cache: bool = False
    cache_parquet_path: Optional[str] = None
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
    engine: str = "pandas_ta"  # pandas_ta | ta_lib
    params: Dict[str, List[int]] = Field(
        default_factory=lambda: {"rsi": [14], "ema": [10, 20, 50], "macd": [12, 26, 9]}
    )


class BenchmarkCfg(BaseModel):
    xu100_source: str = "none"  # csv | none
    xu100_csv_path: Optional[str] = None


class ReportCfg(BaseModel):
    excel: bool = True
    csv: bool = True
    percent_format: str = "0.00%"
    daily_sheet_prefix: str = "SCAN_"
    summary_sheet_name: str = "SUMMARY"


class RootCfg(BaseModel):
    project: ProjectCfg
    data: DataCfg
    calendar: CalendarCfg = Field(default_factory=CalendarCfg)  # TİP DÜZELTİLDİ
    indicators: IndicatorsCfg = Field(default_factory=IndicatorsCfg)  # TİP DÜZELTİLDİ
    benchmark: BenchmarkCfg = Field(default_factory=BenchmarkCfg)  # TİP DÜZELTİLDİ
    report: ReportCfg = Field(default_factory=ReportCfg)  # TİP DÜZELTİLDİ


def load_config(path: str | Path) -> RootCfg:
    p = resolve_path(path)
    if not p.exists():
        warnings.warn(f"Config bulunamadı: {p}")
        return RootCfg(
            project=ProjectCfg(),
            data=DataCfg(excel_dir="", filters_csv=""),
        )
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise TypeError("Config içeriği sözlük olmalı")  # TİP DÜZELTİLDİ
    base = p.parent

    def _join(v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        raw = os.path.expandvars(os.path.expanduser(v))
        vp = Path(raw)
        if not vp.is_absolute():
            vp = base / vp
        return str(resolve_path(vp))

    proj = cfg.get("project", {}) if isinstance(cfg, dict) else {}
    if isinstance(proj, dict) and proj.get("out_dir"):
        proj["out_dir"] = _join(proj.get("out_dir"))  # PATH DÜZENLENDİ
    data = cfg.get("data", {}) if isinstance(cfg, dict) else {}
    for k in ["excel_dir", "filters_csv", "cache_parquet_path"]:
        v = data.get(k)
        if v:
            data[k] = _join(v)  # PATH DÜZENLENDİ
    cal = cfg.get("calendar", {}) if isinstance(cfg, dict) else {}
    if isinstance(cal, dict) and cal.get("holidays_csv_path"):
        cal["holidays_csv_path"] = _join(cal.get("holidays_csv_path"))  # PATH DÜZENLENDİ
    bench = cfg.get("benchmark", {}) if isinstance(cfg, dict) else {}
    if isinstance(bench, dict) and bench.get("xu100_csv_path"):
        bench["xu100_csv_path"] = _join(bench.get("xu100_csv_path"))  # PATH DÜZENLENDİ
    cfg["project"], cfg["data"], cfg["calendar"], cfg["benchmark"] = proj, data, cal, bench
    return RootCfg(**cfg)
