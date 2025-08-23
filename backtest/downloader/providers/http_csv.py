from __future__ import annotations

import io
from datetime import date
from typing import Any

import pandas as pd
import requests

from .base import BaseProvider


class HTTPCSVProvider(BaseProvider):
    name = "http_csv"

    def __init__(self, url_template: str, timeout: int = 10) -> None:
        self.url_template = url_template
        self.timeout = timeout

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        url = self.url_template.format(symbol=symbol, start=start, end=end)
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]
        return df
