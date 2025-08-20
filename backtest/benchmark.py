from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger


class BenchmarkLoader:
    """Load benchmark price data according to configuration."""

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def load(self) -> pd.DataFrame | None:
        """Return normalized ``date``/``close`` benchmark data or ``None``.

        The loader supports three sources controlled by ``cfg['source']``:

        ``none``
            Benchmark disabled; return ``None`` without logging.
        ``excel``
            Read from :func:`pandas.read_excel` using ``excel_path`` and
            ``excel_sheet``.
        ``csv``
            Read from :func:`pandas.read_csv` using ``csv_path``.
        """

        src = (self.cfg.get("source") or "none").lower()
        if src == "none":
            return None
        if src == "excel":
            path = Path(self.cfg.get("excel_path", ""))
            sheet = self.cfg.get("excel_sheet", "BIST")
            if not path.exists():
                msg = (
                    f"benchmark excel not found: {path}. "
                    "Config'te 'benchmark.excel_path' ayarını kontrol edin."
                )
                logger.error(msg)
                raise FileNotFoundError(msg)
            df = pd.read_excel(path, sheet_name=sheet)
        elif src == "csv":
            path = Path(self.cfg.get("csv_path", ""))
            if not path.exists():
                msg = (
                    f"benchmark csv not found: {path}. "
                    "Config'te 'benchmark.csv_path' ayarını kontrol edin."
                )
                logger.error(msg)
                raise FileNotFoundError(msg)
            df = pd.read_csv(path)
        else:
            raise ValueError(f"unknown benchmark source: {src}")

        date_col = self.cfg.get("column_date", "date")
        close_col = self.cfg.get("column_close", "close")
        df = df[[date_col, close_col]].rename(
            columns={date_col: "date", close_col: "close"}
        )
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df.sort_values("date").dropna()
        if df.empty:
            raise ValueError("benchmark data empty")
        logger.info(
            "benchmark loaded rows={} first={} last={}",
            len(df),
            df["date"].iloc[0],
            df["date"].iloc[-1],
        )
        return df


__all__ = ["BenchmarkLoader"]
