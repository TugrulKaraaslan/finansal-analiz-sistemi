"""Create and update the project's Parquet cache.

CSV files under ``veri/ham`` are concatenated into one Parquet file at
``config.PARQUET_CACHE_PATH``.  A :class:`filelock.FileLock` guards the write
operation so concurrent runs remain safe. Existing caches are reused on
subsequent runs.
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
    """Compile CSV files under ``RAW_DIR`` into the Parquet cache.

    All CSV files are concatenated into a single dataset and written to
    ``CACHE``.  A :class:`filelock.FileLock` ensures concurrent runs do not
    corrupt the file. Existing caches are left untouched.
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
