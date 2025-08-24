from __future__ import annotations

import io
import os
from datetime import date

import pandas as pd
import requests

from .base import BaseProvider


class HttpCSVProvider(BaseProvider):
    name = "http_csv"

    def __init__(self, url_template: str, timeout: int = 10, allow_download: bool | None = None) -> None:
        self.url_template = url_template
        self.timeout = timeout
        if allow_download is None:
            allow_download = os.getenv("ALLOW_DOWNLOAD") == "1"
        self.allow_download = allow_download

    def fetch(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        if not self.allow_download:
            raise RuntimeError(
                "Downloads are disabled by default; use --allow-download or ALLOW_DOWNLOAD=1"
            )
        url = self.url_template.format(symbol=symbol, start=start, end=end)
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            mask = (df["date"] >= start) & (df["date"] <= end)
            df = df.loc[mask]
        return df
