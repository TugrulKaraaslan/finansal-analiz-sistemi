from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from backtest.indicators.compute import (
    ensure_cci,
    ensure_mom,
    ensure_roc,
    ensure_stochrsi,
)

_STOCHRSI_RE = re.compile(r"stochrsi_[kd]_(\d+)_(\d+)_(\d+)_(\d+)")
_MOM_RE = re.compile(r"mom_(\d+)")
_ROC_RE = re.compile(r"roc_(\d+)")
_CCI_RE = re.compile(r"cci_(\d+)")


def precompute_needed(df: pd.DataFrame, series: Iterable[str]) -> pd.DataFrame:
    """Compute indicator series required by ``series`` names."""

    for name in series:
        m = _STOCHRSI_RE.fullmatch(name)
        if m:
            rsi_len, k, d, smooth = map(int, m.groups())
            df = ensure_stochrsi(df, rsi_len, k, d, smooth)
            continue
        m = _MOM_RE.fullmatch(name)
        if m:
            df = ensure_mom(df, int(m.group(1)))
            continue
        m = _ROC_RE.fullmatch(name)
        if m:
            df = ensure_roc(df, int(m.group(1)))
            continue
        m = _CCI_RE.fullmatch(name)
        if m:
            df = ensure_cci(df, int(m.group(1)))
            continue
    return df


__all__ = ["precompute_needed"]
