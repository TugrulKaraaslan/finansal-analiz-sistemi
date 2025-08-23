from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .base import BaseProvider


class LocalExcelProvider(BaseProvider):
    name = "local_excel"

    def __init__(self, directory: str | Path, sheet: str | None = None) -> None:
        self.directory = Path(directory)
        self.sheet = sheet

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        path = self.directory / f"{symbol}.xlsx"
        df = pd.read_excel(path, sheet_name=self.sheet)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]
        return df
