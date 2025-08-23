from __future__ import annotations

from datetime import date
from typing import List, Tuple

import pandas as pd

from .base import BaseProvider


class StubProvider(BaseProvider):
    """Provider generating deterministic synthetic data for tests."""

    name = "stub"

    def __init__(self) -> None:
        self.calls: List[Tuple[str, date, date]] = []

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        self.calls.append((symbol, start, end))
        dates = pd.date_range(start, end, freq="B")
        n = len(dates)
        data = {
            "date": dates,
            "open": [1.0] * n,
            "high": [2.0] * n,
            "low": [0.5] * n,
            "close": [1.5] * n,
            "volume": list(range(n)),
            "quantity": list(range(n)),
        }
        return pd.DataFrame(data)
