from __future__ import annotations

import logging
from typing import List, Tuple

import pandas as pd

from backtest.naming import normalize_name
from .cross import cross_up, cross_down, cross_over, cross_under

logger = logging.getLogger(__name__)


SERIES_SERIES_CROSSOVERS: List[Tuple[str, str, str, str]] = [
    (
        "sma_10",
        "sma_50",
        "sma_10_keser_sma_50_yukari",
        "sma_10_keser_sma_50_asagi",
    ),
]

SERIES_VALUE_CROSSOVERS: List[Tuple[str, float, str, str]] = [
    ("adx_14", 20.0, "adx_14_keser_20p0_yukari", "adx_14_keser_20p0_asagi"),
]


def generate_crossovers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for a, b, up, down in SERIES_SERIES_CROSSOVERS:
        a_c = normalize_name(a)
        b_c = normalize_name(b)
        if a_c not in out.columns or b_c not in out.columns:
            missing = [x for x in (a_c, b_c) if x not in out.columns]
            logger.warning("skip crossover: missing column(s) %s", ", ".join(missing))
            continue
        out[up] = cross_up(out[a_c], out[b_c])
        out[down] = cross_down(out[a_c], out[b_c])
    for a, val, up, down in SERIES_VALUE_CROSSOVERS:
        a_c = normalize_name(a)
        if a_c not in out.columns:
            logger.warning("skip crossover: missing column(s) %s", a_c)
            continue
        out[up] = cross_over(out[a_c], val)
        out[down] = cross_under(out[a_c], val)
    return out


__all__ = [
    "generate_crossovers",
    "SERIES_SERIES_CROSSOVERS",
    "SERIES_VALUE_CROSSOVERS",
]
