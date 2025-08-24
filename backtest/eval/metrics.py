from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# --- Sinyal metrikleri ---


def rolling_future_return(prices: pd.Series, horizon_days: int = 5) -> pd.Series:
    """İleriye dönük basit getiri: (P[t+h]/P[t] - 1). Son h bar için NaN döner."""
    fwd = prices.shift(-horizon_days)
    ret = (fwd / prices) - 1.0
    ret.iloc[-horizon_days:] = np.nan
    return ret


@dataclass
class SignalMetricConfig:
    horizon_days: int = 5
    threshold_bps: float = 50.0  # 50 bps = %0.5
    side: str = "long"  # long|short
    price_col: str = "close"


@dataclass
class Confusion:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def precision(self):
        return self.tp / max(self.tp + self.fp, 1)

    @property
    def recall(self):
        return self.tp / max(self.tp + self.fn, 1)

    @property
    def f1(self):
        p, r = self.precision, self.recall
        return 2 * p * r / max(p + r, 1e-12)


def confusion_from_signals(
    prices: pd.Series, signals: pd.Series, cfg: SignalMetricConfig
) -> tuple[Confusion, pd.DataFrame]:
    prices = prices.astype(float)
    sig = signals.fillna(False).astype(bool)
    fwd = rolling_future_return(prices, cfg.horizon_days)
    thr = cfg.threshold_bps * 1e-4
    if cfg.side == "long":
        y_true = fwd >= thr
    else:  # short
        y_true = fwd <= -thr
    y_pred = sig

    valid = y_true.notna()
    y_true = y_true[valid]
    y_pred = y_pred[valid]

    tp = int(((y_pred == True) & (y_true == True)).sum())
    fp = int(((y_pred == True) & (y_true == False)).sum())
    tn = int(((y_pred == False) & (y_true == False)).sum())
    fn = int(((y_pred == False) & (y_true == True)).sum())

    detail = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})
    return Confusion(tp, fp, tn, fn), detail


def signal_metrics_for_filter(df: pd.DataFrame, signal_col: str, cfg: SignalMetricConfig) -> dict:
    prices = df[cfg.price_col]
    sig = df[signal_col]
    cm, _ = confusion_from_signals(prices, sig, cfg)
    return {
        "signal": signal_col,
        "horizon_days": cfg.horizon_days,
        "threshold_bps": cfg.threshold_bps,
        "precision": round(cm.precision, 6),
        "recall": round(cm.recall, 6),
        "f1": round(cm.f1, 6),
        "tp": cm.tp,
        "fp": cm.fp,
        "tn": cm.tn,
        "fn": cm.fn,
    }


# --- Portföy metrikleri ---


def daily_returns_from_equity(eq: pd.Series) -> pd.Series:
    e = eq.astype(float)
    r = e.pct_change().dropna()
    return r


def cagr(eq: pd.Series) -> float:
    e0, e1 = float(eq.iloc[0]), float(eq.iloc[-1])
    days = (eq.index[-1] - eq.index[0]).days or (len(eq) - 1)
    years = max(days / 365.25, 1e-9)
    return (e1 / max(e0, 1e-12)) ** (1 / years) - 1


def volatility_ann(r: pd.Series, freq: int = 252) -> float:
    return float(r.std(ddof=0) * math.sqrt(freq))


def sharpe(r: pd.Series, rf: float = 0.0, freq: int = 252) -> float:
    ex = r - (rf / freq)
    vol = volatility_ann(r, freq)
    return float((ex.mean() * freq) / max(vol, 1e-12))


def sortino(r: pd.Series, rf: float = 0.0, freq: int = 252) -> float:
    ex = r - (rf / freq)
    downside = r[r < 0]
    dvol = float(downside.std(ddof=0) * math.sqrt(freq))
    return float((ex.mean() * freq) / max(dvol, 1e-12))


def max_drawdown(eq: pd.Series) -> tuple[float, int]:
    e = eq.astype(float)
    peak = e.cummax()
    dd = e / peak - 1.0
    mdd = float(dd.min())  # negatif değer
    # süre tahmini: en uzun toparlanma periyodu
    dur = 0
    max_dur = 0
    for v in dd:
        if v < 0:
            dur += 1
        else:
            max_dur = max(max_dur, dur)
            dur = 0
    max_dur = max(max_dur, dur)
    return mdd, max_dur


def hit_rate_from_trades(trades: pd.DataFrame) -> tuple[float, float, float]:
    if trades is None or trades.empty:
        return (float("nan"), float("nan"), float("nan"))
    if not {"pnl"}.issubset(set(trades.columns)):
        return (float("nan"), float("nan"), float("nan"))
    pnl = trades["pnl"].astype(float)
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    hr = float((len(wins) / max(len(pnl), 1)))
    avgw = float(wins.mean()) if len(wins) > 0 else float("nan")
    avgl = float(losses.mean()) if len(losses) > 0 else float("nan")
    return hr, avgw, avgl


def equity_metrics(eq_df: pd.DataFrame, equity_col: str = "equity") -> dict:
    if equity_col not in eq_df.columns:
        raise ValueError(f"missing column: {equity_col}")
    eq = eq_df.set_index(pd.to_datetime(eq_df["date"]))[equity_col]
    r = daily_returns_from_equity(eq)
    mdd, mdd_dur = max_drawdown(eq)
    c = cagr(eq)
    vol = volatility_ann(r)
    sh = sharpe(r)
    so = sortino(r)
    mar = c / abs(mdd) if mdd < 0 else float("inf")
    return {
        "cagr": c,
        "vol": vol,
        "sharpe": sh,
        "sortino": so,
        "max_drawdown": mdd,
        "max_dd_days": mdd_dur,
        "mar": mar,
    }
