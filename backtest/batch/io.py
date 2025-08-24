from __future__ import annotations

from pathlib import Path

import pandas as pd


class OutputWriter:
    def __init__(self, out_dir: str | Path):
        self.root = Path(out_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_day(self, day, rows: list[tuple[str, str]]):
        """rows: [(symbol, filter_code), ...]"""
        p = self.root / f"{pd.to_datetime(day).date()}.csv"
        if not rows:
            # Boş gün de dosyalanır (görülebilirlik için)
            df = pd.DataFrame(columns=["date", "symbol", "filter_code"])
            df.to_csv(p, index=False)
            return p
        df = pd.DataFrame(rows, columns=["symbol", "filter_code"])
        df.insert(0, "date", pd.to_datetime(day).date())
        df.drop_duplicates(subset=["date", "symbol", "filter_code"], inplace=True)
        df.to_csv(p, index=False)
        return p
