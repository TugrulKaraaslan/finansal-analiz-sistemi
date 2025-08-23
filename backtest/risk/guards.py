from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os
import json
import math
import time
import pandas as pd


@dataclass
class GuardResult:
    action: str  # 'allow' | 'modify' | 'block'
    reason: str
    details: dict = field(default_factory=dict)


@dataclass
class RiskDecision:
    final_action: str  # 'allow' | 'modify' | 'block'
    reasons: list[GuardResult]


class RiskEngine:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    # ---- helpers ----
    def _kill_switch(self) -> GuardResult | None:
        env = self.cfg.get("kill_switch_env", "KILL_SWITCH")
        if os.getenv(env, "0") in ("1", "true", "TRUE", "on", "ON"):
            return GuardResult("block", "kill_switch", {"env": env})
        return None

    def _cb_intraday_dd(self, state) -> GuardResult | None:
        bps = float(
            self.cfg.get("circuit_breakers", {}).get(
                "max_intraday_dd_bps", float("inf")
            )
        )
        if not math.isfinite(bps):
            return None
        if state.get("intraday_dd_bps", 0.0) <= -abs(bps):
            return GuardResult(
                "block",
                "intraday_drawdown",
                {"dd_bps": state["intraday_dd_bps"], "limit_bps": -abs(bps)},
            )
        return None

    def _cb_max_trades(self, state) -> GuardResult | None:
        lim = int(
            self.cfg.get("circuit_breakers", {}).get("max_daily_trades", 10**9)
        )  # noqa: E501
        if state.get("daily_trades", 0) >= lim:
            return GuardResult(
                "block",
                "max_daily_trades",
                {"count": state["daily_trades"], "limit": lim},
            )
        return None

    def _cb_volatility(self, mkt_row: pd.Series) -> GuardResult | None:
        vol = self.cfg.get("circuit_breakers", {}).get("volatility_halt", {})
        if not vol:
            return None
        wnd = int(vol.get("atr_window", 14))
        thr_bps = float(vol.get("atr_to_price_bps", float("inf")))
        atr = (
            mkt_row.get(f"atr_{wnd}") or mkt_row.get("atr")
            if mkt_row is not None
            else None
        )
        close = mkt_row.get("close") if mkt_row is not None else None
        if atr is not None and close:
            ratio_bps = (float(atr) / float(close)) * 1e4
            if ratio_bps >= thr_bps:
                return GuardResult(
                    "block",
                    "volatility_halt",
                    {"ratio_bps": ratio_bps, "thr_bps": thr_bps},
                )
        return None

    def _exposure_caps(
        self, proposed_notional: float, equity: float, symbol_exposure: float
    ) -> GuardResult | None:
        ex = self.cfg.get("exposure", {})
        per_sym = float(ex.get("per_symbol_max_pct", 1.0))
        cap_cash = equity * per_sym
        if abs(proposed_notional) > cap_cash:
            new_notional = math.copysign(cap_cash, proposed_notional)
            return GuardResult(
                "modify",
                "per_symbol_cap",
                {
                    "old": proposed_notional,
                    "new": new_notional,
                    "cap_cash": cap_cash,
                },
            )
        return None

    # ---- ana karar ----
    def decide(
        self,
        state: dict,
        orders_df: pd.DataFrame,
        mkt_row: pd.Series | None,
        equity: float,
        symbol_exposure: float,
    ) -> RiskDecision:
        reasons: list[GuardResult] = []
        for chk in (
            self._kill_switch,
            lambda: self._cb_intraday_dd(state),
            lambda: self._cb_max_trades(state),
        ):
            r = chk() if callable(chk) else None
            if r:
                reasons.append(r)
        if mkt_row is not None:
            r = self._cb_volatility(mkt_row)
            if r:
                reasons.append(r)
        if (
            equity
            and not orders_df.empty
            and "fill_price" in orders_df.columns
            and "quantity" in orders_df.columns
        ):
            notional = float(
                (orders_df["fill_price"] * orders_df["quantity"]).sum()
            )  # noqa: E501
            r = self._exposure_caps(notional, equity, symbol_exposure)
            if r:
                reasons.append(r)
        final = "allow"
        if any(x.action == "block" for x in reasons):
            final = "block"
        elif any(x.action == "modify" for x in reasons):
            final = "modify"
        return RiskDecision(final, reasons)

    def write_report(self, decision: RiskDecision, outdir: Path):
        outdir.mkdir(parents=True, exist_ok=True)
        rec = {
            "final_action": decision.final_action,
            "reasons": [
                dict(action=r.action, reason=r.reason, details=r.details)
                for r in decision.reasons
            ],
            "ts": int(time.time()),
        }
        (outdir / "risk_report.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8"
        )
