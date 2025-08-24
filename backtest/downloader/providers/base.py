from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import pandas as pd


class BaseProvider(ABC):
    """Abstract provider fetching raw data frames."""

    name = "base"

    @abstractmethod
    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        raise NotImplementedError
