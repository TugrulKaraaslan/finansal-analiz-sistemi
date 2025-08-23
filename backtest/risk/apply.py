from __future__ import annotations
from pathlib import Path
import pandas as pd
import os
import yaml
from .guards import RiskEngine

_DEF = {
    "enabled": True,
    "report": {
        "output_dir": "artifacts/risk",
        "write_json": True,
        "write_last_decision": True,
    },
}


def _env_override(cfg: dict, prefix: str = "RISK_") -> dict:
    out = cfg.copy()
    for k, v in os.environ.items():
        if not k.startswith(prefix):
            continue
        keys = k[len(prefix) :].lower().split("__")  # noqa: E203
        cur = out
        for part in keys[:-1]:
            cur = cur.setdefault(part, {})
        try:
            cur[keys[-1]] = yaml.safe_load(v)
        except Exception:
            cur[keys[-1]] = v
    return out


def load_risk_cfg(p: Path | None) -> dict:
    cfg = _DEF
    if p and p.exists():
        cfg = yaml.safe_load(p.read_text()) or {}
    cfg = {**_DEF, **cfg}
    return _env_override(cfg)


def run_risk(
    engine: RiskEngine,
    state: dict,
    orders: pd.DataFrame,
    mkt_row: pd.Series | None,
    equity: float,
    symbol_exposure: float,
    out_dir: Path,
    dry_run: bool,
) -> tuple[pd.DataFrame, str]:
    dec = engine.decide(state, orders, mkt_row, equity, symbol_exposure)
    if out_dir:
        engine.write_report(dec, out_dir)
    if dec.final_action == "block" and not dry_run:
        return orders.iloc[0:0], "blocked"
    if dec.final_action == "modify":
        mods = [r for r in dec.reasons if r.reason == "per_symbol_cap"]
        if mods:
            ratio = abs(mods[-1].details["new"]) / max(
                abs(mods[-1].details["old"]), 1e-9
            )
            orders = orders.copy()
            orders["quantity"] = (orders["quantity"] * ratio).astype(int)
    return orders, dec.final_action
