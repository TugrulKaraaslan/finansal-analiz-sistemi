"""Build the Parquet cache from raw CSV files.

Raw CSV datasets are combined into a single Parquet file that can be
loaded efficiently by the rest of the project.
"""

from pathlib import Path

import pandas as pd
from filelock import FileLock
from loguru import logger

from finansal_analiz_sistemi import config

RAW_DIR = Path("veri/ham")
CACHE = Path(config.PARQUET_CACHE_PATH)
LOCK_FILE = CACHE.with_suffix(".lock")


def build() -> None:
    """Build the Parquet cache when the file is missing or empty.

    All CSV files under :data:`RAW_DIR` are concatenated and written to
    :data:`CACHE` as a Parquet dataset.
    """
    with FileLock(str(LOCK_FILE)):
        if CACHE.exists() and CACHE.stat().st_size > 0:
            logger.info("Cache hit, skipping build")
            return
        logger.info("CSV \u279c Parquet \u00f6nbellek olusturuluyor…")
        dfs = [pd.read_csv(p, parse_dates=["date"]) for p in RAW_DIR.glob("*.csv")]
        if not dfs:
            logger.warning("Ham CSV bulunamadi: %s", RAW_DIR)
            df = pd.DataFrame()
        else:
            df = (
                pd.concat(dfs, ignore_index=True)
                .drop_duplicates(["ticker", "date"])
                .sort_values(["ticker", "date"])
            )
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(CACHE, index=False)
        logger.success("Parquet cache yazildi (%d satir)", len(df))
