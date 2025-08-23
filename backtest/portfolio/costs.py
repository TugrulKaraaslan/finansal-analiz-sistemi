from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import yaml


@dataclass
class CostParams:
    enabled: bool = True
    currency: str = "TRY"
    cash_decimals: int = 2
    commission_model: str = "fixed_bps"
    commission_bps: float = 5.0
    commission_min_cash: float = 0.0
    tax_bps: float = 0.0
    spread_model: str = "half_spread"
    default_spread_bps: float = 7.0
    slippage_model: str = "atr_linear"
    bps_per_1x_atr: float = 10.0
    price_col: str = "fill_price"
    qty_col: str = "quantity"
    side_col: str = "side"
    date_col: str = "date"
    id_col: str = "trade_id"
    write_breakdown: bool = True
    output_dir: str = "artifacts/costs"

    @staticmethod
    def from_yaml(p: Path | None) -> "CostParams":
        if p is None or not p.exists():
            return CostParams()
        cfg = yaml.safe_load(p.read_text()) or {}
        # shallow map
        return CostParams(
            enabled=cfg.get("enabled", True),
            currency=cfg.get("currency", "TRY"),
            cash_decimals=int(cfg.get("rounding", {}).get("cash_decimals", 2)),
            commission_model=cfg.get("commission", {}).get(
                "model", "fixed_bps"
            ),  # noqa: E501
            commission_bps=float(cfg.get("commission", {}).get("bps", 5.0)),
            commission_min_cash=float(
                cfg.get("commission", {}).get("min_cash", 0.0)
            ),  # noqa: E501
            tax_bps=float(cfg.get("taxes", {}).get("bps", 0.0)),
            spread_model=cfg.get("spread", {}).get("model", "half_spread"),
            default_spread_bps=float(
                cfg.get("spread", {}).get("default_spread_bps", 7.0)
            ),
            slippage_model=cfg.get("slippage", {}).get("model", "atr_linear"),
            bps_per_1x_atr=float(
                cfg.get("slippage", {}).get("bps_per_1x_atr", 10.0)
            ),  # noqa: E501
            price_col=cfg.get("apply", {}).get("price_col", "fill_price"),
            qty_col=cfg.get("apply", {}).get("qty_col", "quantity"),
            side_col=cfg.get("apply", {}).get("side_col", "side"),
            date_col=cfg.get("apply", {}).get("date_col", "date"),
            id_col=cfg.get("apply", {}).get("id_col", "trade_id"),
            write_breakdown=cfg.get("report", {}).get("write_breakdown", True),
            output_dir=cfg.get("report", {}).get(
                "output_dir", "artifacts/costs"
            ),  # noqa: E501
        )


BPS = 1e-4


def _sgn(side: str) -> int:
    return 1 if str(side).upper().startswith("B") else -1


# Komisyon (cash)
def commission_cash(notional: pd.Series, params: CostParams) -> pd.Series:
    if params.commission_model == "fixed_bps":
        cash = notional.abs() * (params.commission_bps * BPS)
        if params.commission_min_cash > 0:
            cash = cash.where(
                cash >= params.commission_min_cash, params.commission_min_cash
            )
        return cash
    elif params.commission_model == "per_share_flat":
        # per-share  => notional yerine adet başına sabit
        return pd.Series(0.0, index=notional.index)
    return pd.Series(0.0, index=notional.index)


# Spread & Slippage bps
def effective_bps(df: pd.DataFrame, params: CostParams) -> pd.Series:
    eff = pd.Series(0.0, index=df.index)
    # Spread
    if params.spread_model == "fixed_bps":
        eff += params.default_spread_bps
    elif params.spread_model == "half_spread":
        eff += params.default_spread_bps * 0.5
    # Slippage
    if params.slippage_model == "fixed_bps":
        eff += 0.0
    elif params.slippage_model == "atr_linear":
        # ATR/Close oranı varsa kullan, yoksa default 0
        atr = None
        for c in ["atr_14", "ATR_14", "atr"]:
            if c in df.columns:
                atr = df[c]
                break
        close = df.get("close")
        if atr is not None and close is not None:
            ratio = (atr / close).clip(lower=0, upper=0.2).fillna(0.0)
            eff += ratio * params.bps_per_1x_atr * 1.0
    return eff


# Ana fonksiyon: trade satırına maliyeti uygula
# trades_df sütunları: price_col, qty_col, side_col (+isteğe bağlı close/atr)


def apply_costs(trades_df: pd.DataFrame, params: CostParams) -> pd.DataFrame:
    if trades_df is None or trades_df.empty or not params.enabled:
        return trades_df.copy()
    df = trades_df.copy()
    price = df[params.price_col].astype(float)
    qty = df[params.qty_col].astype(float)
    df[params.side_col] = df[params.side_col].astype(str)

    notional = price * qty
    comm = commission_cash(notional, params)
    effbps = effective_bps(df, params)
    slip_cash = notional.abs() * (effbps * BPS)
    tax_cash = notional.abs() * (params.tax_bps * BPS)

    total_cost = (comm + slip_cash + tax_cash).round(params.cash_decimals)

    df["cost_commission"] = comm.round(params.cash_decimals)
    df["cost_slippage"] = slip_cash.round(params.cash_decimals)
    df["cost_taxes"] = tax_cash.round(params.cash_decimals)
    df["cost_total"] = total_cost
    df["notional"] = notional

    # Net fiyat (alımda +, satımda - yönle ilişkili değil; raporlama için):
    df["net_price"] = (notional + _sgn("BUY") * 0) / qty  # placeholder

    if params.write_breakdown:
        out_dir = Path(params.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime

        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        df.to_csv(out_dir / f"costs_{ts}.csv", index=False)

    return df
