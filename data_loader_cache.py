"""
In-memory cache for CSV and Excel files.

Entries are keyed by absolute path and file metadata so repeated reads
avoid disk access. Each cached dataset expires after ``ttl`` seconds.
"""

import os

import pandas as pd
from cachetools import TTLCache

from finansal_analiz_sistemi import config
from src.utils.excel_reader import open_excel_cached


class DataLoaderCache:
    """Cache CSV and Excel files in memory to avoid redundant disk reads.

    File modification time and size are tracked so cached entries are
    transparently refreshed whenever the source file changes.
    """

    def __init__(self, logger=None, *, ttl: int = 4 * 60 * 60, maxsize: int = 64):
        """Initialize the cache and configure expiration policy.

        Parameters
        ----------
        logger : logging.Logger, optional
            Logger used for debug messages.
        ttl : int, optional
            Time-to-live for cached entries in seconds.
        maxsize : int, optional
            Maximum number of cached datasets.

        Returns
        -------
        None
        """
        self.loaded_data: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.logger = logger

    def clear(self) -> None:
        """Clear the internal cache.

        All cached datasets are removed immediately.
        """
        self.loaded_data.clear()

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Return ``filepath`` as a DataFrame using the in-memory cache.

        The file is reloaded only when its modification time or size changes.

        Parameters
        ----------
        filepath : str
            CSV file path.
        **kwargs
            Options forwarded to :func:`pandas.read_csv`.

        Returns
        -------
        pd.DataFrame
            Data read from disk or returned from the cache.
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
        """Return an ``ExcelFile`` object loaded through the cache.

        The workbook is read from disk only when no cached entry exists or the
        stored version has expired. The absolute path forms the cache key so
        repeated calls with the same file avoid I/O when possible.

        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        **kwargs
            Additional options forwarded to :class:`pandas.ExcelFile`.

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
