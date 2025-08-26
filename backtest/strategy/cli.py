from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from backtest.cv.timeseries import PurgedKFold, WalkForward, cross_validate

from . import StrategyRegistry, StrategySpec, run_strategy
from io_filters import get_filters


def compare_strategies_cli(args) -> None:
    """CLI entry for comparing multiple strategies."""

    filters_df = pd.DataFrame(get_filters())
    reg, _constraints = StrategyRegistry.load_from_file(args.space, filters_df)
    dates = pd.date_range(args.start, args.end, freq="B")
    np.random.seed(0)
    data = pd.DataFrame({"returns": np.random.normal(0, 0.01, len(dates))}, index=dates)
    records = []
    for spec in reg._strategies.values():
        res = run_strategy(spec, data, exec_cfg=None)
        records.append({"id": spec.id, **res.metrics})
    out_dir = Path("artifacts/compare")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(out_dir / "results.csv", index=False)
    (out_dir / "summary.html").write_text(df.to_html(index=False), encoding="utf-8")


def _grid(space: dict) -> itertools.product:
    keys = list(space.keys())
    values = [v.get("grid", [0]) for v in space.values()]
    for combo in itertools.product(*values):
        yield dict(zip(keys, combo))


def _random(space: dict, rng: np.random.Generator) -> dict:
    params = {}
    for k, v in space.items():
        if "grid" in v:
            params[k] = rng.choice(v["grid"])
        elif "randint" in v:
            low = v["randint"]["low"]
            high = v["randint"]["high"]
            params[k] = int(rng.integers(low, high))
    return params


def tune_strategy_cli(args) -> None:
    """CLI entry for tuning a strategy via simple search."""

    cfg = yaml.safe_load(Path(args.space).read_text())
    s_cfg = cfg["strategy"]
    strategy_id = s_cfg["id"]
    base_filters = s_cfg.get("base_filters", [])
    space = s_cfg.get("space", {})
    constraints = cfg.get("constraints", {})
    cv_cfg = cfg.get("cv", {})
    folds = int(cv_cfg.get("folds", 3))
    embargo = int(cv_cfg.get("embargo_days", 0))
    kind = cv_cfg.get("kind", "walk-forward")

    rng = np.random.default_rng(args.seed)
    dates = pd.date_range(args.start, args.end, freq="B")
    data = pd.DataFrame({"returns": rng.normal(0, 0.01, len(dates))}, index=dates)

    if args.search == "grid":
        iterator = _grid(space)
    else:
        iterator = (_random(space, rng) for _ in range(args.max_iters))

    best_score = -1e9
    best_params: dict = {}
    records = []
    for i, params in enumerate(iterator):
        if i >= args.max_iters:
            break
        spec = StrategySpec(id=strategy_id, filters=base_filters, params=params)
        splitter = (
            PurgedKFold(n_splits=folds, embargo=embargo)
            if kind == "purged-kfold"
            else WalkForward(folds=folds, embargo=embargo)
        )
        scores = cross_validate(spec, data, splitter, constraints)
        mean_score = float(np.mean(scores))
        rec = {"iter": i, **params, "score": mean_score}
        records.append(rec)
        if mean_score > best_score:
            best_score = mean_score
            best_params = params
    out_dir = Path("artifacts/tune")
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(out_dir / "best_config.json").write_text(json.dumps(best_params), encoding="utf-8")
    pd.DataFrame(records).to_csv(out_dir / "cv_results.csv", index=False)
    with (out_dir / "progress.jsonl").open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
