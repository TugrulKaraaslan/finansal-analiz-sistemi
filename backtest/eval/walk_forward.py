from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json

ISO = "%Y-%m-%d"


@dataclass
class WfParams:
    start: str  # ISO tarih
    end: str  # ISO tarih (dahil)
    train_days: int
    test_days: int
    step_days: int | None = None  # None => test_days
    min_train_days: int | None = None  # None => train_days

    def normalized(self) -> "WfParams":
        step = self.step_days or self.test_days
        mtrain = self.min_train_days or self.train_days
        return WfParams(
            self.start, self.end, self.train_days, self.test_days, step, mtrain
        )


def _d(s: str) -> datetime:
    return datetime.strptime(s, ISO)


def _iso(d: datetime) -> str:
    return d.strftime(ISO)


def generate_folds(p: WfParams) -> list[dict]:
    p = p.normalized()
    ds = _d(p.start)
    de = _d(p.end)
    if de < ds:
        raise ValueError("end < start")

    folds: list[dict] = []
    # test penceresi kayarak ilerler; train her adımda geriye doğru
    # p.train_days
    cur_test_start = ds + timedelta(days=p.train_days)  # ilk testin başlangıcı
    # min train koşulu için en erken test başlangıcı:
    min_test_start = ds + timedelta(days=p.min_train_days)
    if cur_test_start < min_test_start:
        cur_test_start = min_test_start

    while True:
        test_start = cur_test_start
        test_end = test_start + timedelta(days=p.test_days - 1)
        if test_start > de:
            break
        if test_end > de:
            test_end = de
        train_end = test_start - timedelta(days=1)
        train_start = max(ds, train_end - timedelta(days=p.train_days - 1))
        if train_end < train_start:
            break
        folds.append(
            {
                "train_start": _iso(train_start),
                "train_end": _iso(train_end),
                "test_start": _iso(test_start),
                "test_end": _iso(test_end),
            }
        )
        cur_test_start = test_start + timedelta(days=p.step_days)
        if test_start >= de:
            break
    return folds


def save_folds(folds: list[dict], outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / "folds.json"
    p.write_text(json.dumps(folds, indent=2), encoding="utf-8")
    return p
