from __future__ import annotations
from pathlib import Path
import pandas as pd
from .engine import PortfolioParams, generate_orders
from backtest.risk.apply import load_risk_cfg, run_risk
from backtest.risk.guards import RiskEngine

# costs entegrasyonu (opsiyonel)
try:
    from .costs import CostParams, apply_costs
except Exception:  # costs modülü yoksa no-op
    CostParams = None

    def apply_costs(df, params):
        return df


class PortfolioSim:
    def __init__(
        self,
        params: PortfolioParams,
        cost_cfg: Path | None = None,
        risk_cfg: Path | None = None,
    ):
        self.params = params
        self.cost_params = (
            CostParams.from_yaml(cost_cfg) if CostParams else None
        )  # noqa: E501
        self.risk_cfg = load_risk_cfg(risk_cfg or Path("config/risk.yaml"))
        self.risk_engine = (
            RiskEngine(self.risk_cfg)
            if self.risk_cfg.get("enabled", True)
            else None  # noqa: E501
        )
        self.equity = params.initial_equity
        self.positions = {}  # symbol -> qty
        self.trades = []
        self.daily = []

    def step(self, date, signals_day: pd.DataFrame, market_day: pd.DataFrame):
        orders = generate_orders(
            signals_day, market_day, self.params, self.equity
        )  # noqa: E501
        if not orders.empty:
            trades = orders.copy()
            trades["fill_price"] = trades["price"]
            trades["quantity"] = trades["qty"]
            if self.risk_engine:
                mkt_row = (
                    market_day.iloc[0]
                    if hasattr(market_day, "iloc") and len(market_day) > 0
                    else None
                )
                state = {
                    "date": str(date),
                    "equity": self.equity,
                    "intraday_dd_bps": 0.0,
                    "daily_trades": len(trades),
                }
                out_dir = Path(self.params.out_dir).parent / "risk"
                trades, action = run_risk(
                    self.risk_engine,
                    state,
                    trades,
                    mkt_row,
                    self.equity,
                    0.0,
                    out_dir,
                    bool(self.risk_cfg.get("dry_run", True)),
                )
            if not trades.empty:
                trades["side"] = trades["side"].replace(
                    {"BUY": "BUY", "SELL": "SELL", "EXIT": "SELL"}
                )
                if self.cost_params:
                    trades = apply_costs(trades, self.cost_params)
                cash_delta = (trades["fill_price"] * trades["quantity"]).sum()
                self.equity -= cash_delta  # kaba: detaylı PnL akışı sonraki PR
                self.trades.append(trades)
        self.daily.append({"date": date, "equity": self.equity})

    def finalize(self, outdir: Path):
        outdir.mkdir(parents=True, exist_ok=True)
        if self.trades:
            pd.concat(self.trades, ignore_index=True).to_csv(
                outdir / "trades.csv", index=False
            )
        if self.daily:
            pd.DataFrame(self.daily).to_csv(
                outdir / "daily_equity.csv", index=False
            )  # noqa: E501
