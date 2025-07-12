"""In-memory cache for CSV and Excel loaders.

The helper stores file contents keyed by path and modification time so
repeated calls skip disk access when the source has not changed.
"""

import os

import pandas as pd
from cachetools import TTLCache

from finansal_analiz_sistemi import config
from src.utils.excel_reader import open_excel_cached


class DataLoaderCache:
    """In-memory caching wrapper for CSV and Excel loaders.

    The cache tracks file modification time and size to avoid redundant
    disk reads across repeated data-loading operations.
    """

    def __init__(self, logger=None, *, ttl: int = 4 * 60 * 60, maxsize: int = 64):
        """Initialize the cache and configure expiration policy.

        Parameters
        ----------
        logger : optional
            Logger used for debug messages.
        ttl : int, optional
            Time-to-live for cached entries in seconds.
        maxsize : int, optional
            Maximum number of cached datasets.

        """
        self.loaded_data: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.logger = logger

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Return DataFrame from ``filepath`` using a lightweight cache.

        The file is only read again when its modification time or size
        differs from the cached entry so repeated calls avoid disk access.

        Parameters
        ----------
        filepath : str
            CSV file path.
        **kwargs : Any
            Options forwarded to :func:`pandas.read_csv` when reading.

        Returns
        -------
        pd.DataFrame
            DataFrame from cache or newly read from disk.

        """
        abs_path = os.path.abspath(filepath)
        key = (abs_path, "__csv__")
        stat = os.stat(abs_path)
        mtime = stat.st_mtime_ns
        size = stat.st_size
        cached = self.loaded_data.get(key)
        if cached:
            cached_mtime, cached_size, df_cached = cached
            if cached_mtime == mtime and cached_size == size:
                if self.logger:
                    self.logger.debug(f"Cache hit: {key}")
                return df_cached

        try:
            kwargs.setdefault("dtype", config.DTYPES)
            df = pd.read_csv(abs_path, **kwargs)
            self.loaded_data[key] = (mtime, size, df)
            if self.logger:
                self.logger.info(f"CSV yüklendi: {filepath}")
            return df
        except Exception as e:
            if self.logger:
                self.logger.error(f"CSV yükleme hatası: {filepath}: {e}")
            raise

    def load_excel(self, filepath: str, **kwargs) -> pd.ExcelFile:
        """Return a cached ``ExcelFile`` object for ``filepath``.

        The workbook is read from disk when no cached entry exists or when
        the cached version has expired. Results are stored using the absolute
        path as the cache key.

        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        **kwargs : Any
            Additional options forwarded to :func:`pandas.ExcelFile`.

        Returns
        -------
        pd.ExcelFile
            Cached or freshly loaded workbook instance.

        """
        key = (os.path.abspath(filepath), "__excel__")
        if key in self.loaded_data:
            if self.logger:
                self.logger.debug(f"Cache hit: {key}")
            return self.loaded_data[key]

        try:
            xls = open_excel_cached(filepath, **kwargs)
            self.loaded_data[key] = xls
            if self.logger:
                self.logger.info(f"ExcelFile yüklendi: {filepath}")
            return xls
        except Exception as e:
            if self.logger:
                self.logger.error(f"ExcelFile yükleme hatası: {filepath}: {e}")
            raise

    def clear(self) -> None:
        """Clear the internal cache."""
        self.loaded_data.clear()
