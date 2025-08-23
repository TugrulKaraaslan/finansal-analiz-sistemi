from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .base import BaseProvider


class LocalCSVProvider(BaseProvider):
    """Read symbol data from local CSV files."""

    name = "local_csv"

    def __init__(self, directory: str | Path, sep: str = ",", encoding: str = "utf-8") -> None:
        self.directory = Path(directory)
        self.sep = sep
        self.encoding = encoding

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        path = self.directory / f"{symbol}.csv"
        df = pd.read_csv(path, sep=self.sep, encoding=self.encoding)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]
        return df
