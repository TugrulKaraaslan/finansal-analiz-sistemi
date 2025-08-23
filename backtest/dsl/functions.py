from __future__ import annotations
import pandas as pd
from typing import Dict, Callable

from backtest.filters.engine import cross_up, cross_down


# Fonksiyon imzaları: tümü vektörel pandas.Series döndürür


FUNCTIONS: Dict[str, Callable[..., pd.Series]] = {
    "cross_up": cross_up,
    "cross_down": cross_down,
}
