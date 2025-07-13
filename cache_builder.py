"""Build and refresh the project's Parquet cache.

CSV files found in :data:`RAW_DIR` are consolidated into one Parquet file at
:data:`CACHE`. A :class:`filelock.FileLock` protects the write operation so
parallel runs do not corrupt the cache. Subsequent executions reuse this
compiled dataset without touching the raw sources again.
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
    """Build the Parquet cache from the raw CSV files.

    Reads all CSV files under ``RAW_DIR`` and writes them as a single
    Parquet file to ``CACHE``. When an existing cache is found, the
    function returns without rebuilding.

    This helper uses a :class:`filelock.FileLock` to guard writes so
    concurrent runs do not corrupt the cache.
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
