# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path  # TİP DÜZELTİLDİ
import warnings

from pydantic import BaseModel, Field
import yaml


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
    p = Path(path)
    if not p.exists():  # PATH DÜZENLENDİ
        warnings.warn(f"Config bulunamadı: {p}")
        return RootCfg(
            project=ProjectCfg(),
            data=DataCfg(excel_dir="", filters_csv=""),
        )
    with open(p, "r", encoding="utf-8") as f:  # PATH DÜZENLENDİ
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise TypeError("Config içeriği sözlük olmalı")  # TİP DÜZELTİLDİ
    return RootCfg(**cfg)
