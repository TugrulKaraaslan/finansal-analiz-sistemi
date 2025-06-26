"""Parquet cache okuma/yazma ve yenileme mantigi."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import pandas as pd
import portalocker
from pandas import DataFrame

logger: Final[logging.Logger] = logging.getLogger(__name__)


class ParquetCacheManager:  # noqa: D101
    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> DataFrame:  # noqa: D401, D403
        """Load the cached parquet. Raise FileNotFoundError if absent."""
        if not self.cache_path.exists():
            raise FileNotFoundError(self.cache_path)
        df = pd.read_parquet(self.cache_path)
        logger.info("Cache loaded: %s rows", len(df))
        return df

    def refresh(self, csv_path: Path) -> DataFrame:  # noqa: D401, D403
        """Read CSV, write parquet, return DataFrame."""
        import pandas as pd  # local import to speed CLI --help

        with portalocker.Lock(str(self.cache_path) + ".lock", timeout=30):
            df = pd.read_csv(csv_path)
            df.to_parquet(self.cache_path, compression="snappy", index=False)
            logger.info("Cache refreshed from %s (%s rows)", csv_path, len(df))
        return df
