from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .metrics import SignalMetricConfig, equity_metrics, signal_metrics_for_filter

ART = Path("artifacts/metrics")


def save_json(obj, p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


# Sinyal metrikleri (tek df, birden çok filtre kolonu)


def compute_signal_report(
    df: pd.DataFrame, signal_cols: list[str], cfg: SignalMetricConfig
) -> dict:
    rows = [signal_metrics_for_filter(df, c, cfg) for c in signal_cols]
    agg = {
        "avg_precision": float(pd.Series([r["precision"] for r in rows]).mean()),
        "avg_recall": float(pd.Series([r["recall"] for r in rows]).mean()),
        "avg_f1": float(pd.Series([r["f1"] for r in rows]).mean()),
    }
    return {"config": cfg.__dict__, "per_filter": rows, "aggregate": agg}
