"""Manage loading and updating the Parquet cache.

The :class:`ParquetCacheManager` wraps file operations and guards writes
with a lock. Cached data resides at ``config.PARQUET_CACHE_PATH``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

import portalocker

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from pandas import DataFrame

logger: Final[logging.Logger] = logging.getLogger(__name__)


class ParquetCacheManager:
    """Handle loading and refreshing the Parquet cache file."""

    def __init__(self, cache_path: Path) -> None:
        """Initialize with ``cache_path`` and ensure the directory exists."""
        self.cache_path = cache_path
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        """Return ``True`` when the cache file is present."""
        return self.cache_path.is_file()

    def load(self) -> DataFrame:
        """Return the cached Parquet file as a DataFrame."""
        import pandas as pd

        if not self.cache_path.exists():
            raise FileNotFoundError(self.cache_path)
        df = pd.read_parquet(self.cache_path)
        logger.info("Cache loaded: %s rows", len(df))
        return df

    def refresh(self, csv_path: Path) -> DataFrame:
        """Update the cache from ``csv_path`` and return the DataFrame."""
        import pandas as pd  # local import to speed CLI --help

        read_kwargs = {}
        with open(csv_path, encoding="utf-8") as f:
            first_line = f.readline().lstrip()
        if first_line.startswith("#"):
            names = [c.strip() for c in first_line[1:].split(",")]
            read_kwargs = {"comment": "#", "header": None, "names": names}

        with portalocker.Lock(str(self.cache_path) + ".lock", timeout=30):
            df = pd.read_csv(csv_path, **read_kwargs)
            df.to_parquet(self.cache_path, compression="snappy", index=False)
            logger.info("Cache refreshed from %s (%s rows)", csv_path, len(df))
        return df
