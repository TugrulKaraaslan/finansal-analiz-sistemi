from __future__ import annotations

from typing import Callable, Dict

import pandas as pd

from backtest.filters.engine import cross_down, cross_up

# Fonksiyon imzaları: tümü vektörel pandas.Series döndürür


FUNCTIONS: Dict[str, Callable[..., pd.Series]] = {
    "cross_up": cross_up,
    "cross_down": cross_down,
}
