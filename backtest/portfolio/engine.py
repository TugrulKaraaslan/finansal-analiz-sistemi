from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml


@dataclass
class PortfolioParams:
    initial_equity: float = 1_000_000.0
    mode: str = "risk_per_trade"
    risk_per_trade_bps: float = 50.0
    stop_model: str = "atr_multiple"
    atr_period: int = 14
    atr_mult: float = 2.0
    fixed_fraction: float = 0.1
    max_positions: int = 10
    max_position_pct: float = 0.2
    max_gross_exposure: float = 1.0
    allow_short: bool = False
    lot_size: int = 1
    min_qty: int = 1
    round_qty: str = "floor"
    execution_price: str = "close"  # or 'open' or 'custom'
    price_col: str = "close"
    out_dir: str = "artifacts/portfolio"
    write_trades: bool = True
    write_daily: bool = True

    @staticmethod
    def from_yaml(p: Path | None) -> "PortfolioParams":
        if p is None or not p.exists():
            return PortfolioParams()
        cfg = yaml.safe_load(p.read_text()) or {}
        s = cfg.get("sizing", {})
        c = cfg.get("constraints", {})
        pr = cfg.get("pricing", {})
        r = cfg.get("report", {})
        return PortfolioParams(
            initial_equity=float(cfg.get("initial_equity", 1_000_000)),
            mode=s.get("mode", "risk_per_trade"),
            risk_per_trade_bps=float(s.get("risk_per_trade_bps", 50)),
            stop_model=s.get("stop_model", "atr_multiple"),
            atr_period=int(s.get("atr_period", 14)),
            atr_mult=float(s.get("atr_mult", 2.0)),
            fixed_fraction=float(s.get("fixed_fraction", 0.1)),
            max_positions=int(c.get("max_positions", 10)),
            max_position_pct=float(c.get("max_position_pct", 0.2)),
            max_gross_exposure=float(c.get("max_gross_exposure", 1.0)),
            allow_short=bool(c.get("allow_short", False)),
            lot_size=int(c.get("lot_size", 1)),
            min_qty=int(c.get("min_qty", 1)),
            round_qty=str(c.get("round_qty", "floor")),
            execution_price=str(pr.get("execution_price", "close")),
            price_col=str(pr.get("price_col", "close")),
            out_dir=str(r.get("output_dir", "artifacts/portfolio")),
            write_trades=bool(r.get("write_trades", True)),
            write_daily=bool(r.get("write_daily", True)),
        )


# Yardımcı: miktarı lot/min/round’a göre düzelt
_round = {
    "floor": math.floor,
    "round": round,
    "ceil": math.ceil,
}


def adjust_qty(q: float, lot: int, min_qty: int, how: str) -> int:
    q = max(q, min_qty)
    q = _round.get(how, "floor")(q)
    if lot > 1:
        q = (q // lot) * lot
    return int(max(q, 0))


# ATR hesap (gerekirse)


def compute_atr(df: pd.DataFrame, period: int) -> pd.Series:
    if all(c in df.columns for c in ["high", "low", "close"]):
        tr = pd.concat(
            [
                (df["high"] - df["low"]).abs(),
                (df["high"] - df["close"].shift(1)).abs(),
                (df["low"] - df["close"].shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr.rolling(period).mean()
    return pd.Series(np.nan, index=df.index)


# Sizing hesapları


def size_risk_per_trade(
    price: float,
    equity: float,
    params: PortfolioParams,
    atr_val: Optional[float] = None,
) -> int:
    # risk para = equity * bps
    risk_cash = equity * (params.risk_per_trade_bps * 1e-4)
    if params.stop_model == "atr_multiple" and atr_val and atr_val > 0:
        stop_dist = params.atr_mult * atr_val
    else:
        # default: %2 stop
        stop_dist = 0.02 * price
    qty_float = risk_cash / max(stop_dist, 1e-9)
    return adjust_qty(qty_float, params.lot_size, params.min_qty, params.round_qty)  # noqa: E501


def size_fixed_fraction(price: float, equity: float, params: PortfolioParams) -> int:  # noqa: E501
    cash = equity * params.fixed_fraction
    qty_float = cash / max(price, 1e-9)
    return adjust_qty(qty_float, params.lot_size, params.min_qty, params.round_qty)  # noqa: E501


# Emir üretimi: sinyal DataFrame'i kolonları:
# date, symbol, entry_long, exit_long, target_weight (opsiyonel)


def generate_orders(
    signals: pd.DataFrame,
    mkt: pd.DataFrame,
    params: PortfolioParams,
    equity: float,
) -> pd.DataFrame:
    # signals: date,symbol,[entry_long],[exit_long],[target_weight]
    # mkt: date,symbol,close(,high,low)
    mkt_cols = ["date", "symbol", params.price_col, "high", "low", "close"]
    mkt_cols = list(dict.fromkeys(mkt_cols))
    merged = signals.merge(mkt[mkt_cols], on=["date", "symbol"], how="left")
    atr = compute_atr(merged, params.atr_period)
    merged["atr_val"] = atr
    orders = []
    for i, r in merged.iterrows():
        price = float(r.get(params.price_col, np.nan))
        if not np.isfinite(price):
            continue
        if params.mode == "target_weight" and pd.notna(r.get("target_weight")):
            # target_weight → notional = equity * w
            notional = equity * float(r["target_weight"])
            qty = adjust_qty(
                abs(notional) / max(price, 1e-9),
                params.lot_size,
                params.min_qty,
                params.round_qty,
            )
            side = "BUY" if notional > 0 else "SELL"
        elif bool(r.get("entry_long")):
            if params.mode == "risk_per_trade":
                qty = size_risk_per_trade(price, equity, params, r.get("atr_val"))  # noqa: E501
            else:
                qty = size_fixed_fraction(price, equity, params)
            side = "BUY"
        elif bool(r.get("exit_long")):
            qty = 0  # exit; gerçek kapama qty'si runner'dan
            side = "EXIT"
        else:
            continue
        orders.append(
            {
                "date": r["date"],
                "symbol": r["symbol"],
                "side": side,
                "price": price,
                "qty": int(qty),
            }
        )
    return pd.DataFrame(orders)
