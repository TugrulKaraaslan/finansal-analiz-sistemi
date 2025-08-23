from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RiskState:
    date: str
    equity: float
    intraday_dd_bps: float = 0.0
    daily_trades: int = 0
    consec_losses: int = 0

    def on_trade(self, pnl: float):
        if pnl < 0:
            self.consec_losses += 1
        else:
            self.consec_losses = 0
        self.daily_trades += 1
