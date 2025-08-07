from __future__ import annotations

from typing import List, Tuple

# Example crossover definitions
SERIES_SERIES_CROSSOVERS: List[Tuple[str, str]] = [
    ("sma_20", "sma_50"),
    ("sma_50", "sma_200"),
]

SERIES_VALUE_CROSSOVERS: List[Tuple[str, float]] = [
    ("rsi_14", 50.0),
]

__all__ = ["SERIES_SERIES_CROSSOVERS", "SERIES_VALUE_CROSSOVERS"]
