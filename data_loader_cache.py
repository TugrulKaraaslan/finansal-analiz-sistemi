"""
In-memory cache for CSV and Excel files.

Entries are keyed by absolute path and file metadata so repeated reads
avoid disk access. Each cached dataset expires after ``ttl`` seconds.
"""

import os
from dataclasses import dataclass
from typing import Tuple

import pandas as pd
from cachetools import TTLCache

from finansal_analiz_sistemi import config
from src.utils.excel_reader import open_excel_cached


@dataclass
class CachedItem:
    """Metadata and payload for a cached file."""

    mtime: int
    size: int
    data: object


class DataLoaderCache:
    """Cache CSV and Excel files in memory to avoid redundant disk reads.

    File modification time and size are tracked so cached entries are
    transparently refreshed whenever the source file changes.
    """

    def __init__(self, logger=None, *, ttl: int = 4 * 60 * 60, maxsize: int = 64):
        """Initialize the cache and set expiration policy.

        Parameters
        ----------
        logger : logging.Logger, optional
            Logger used for debug messages.
        ttl : int, optional
            Entry lifetime in seconds.
        maxsize : int, optional
            Maximum number of cached datasets.
        """
        self.loaded_data: TTLCache[tuple[str, str], CachedItem] = TTLCache(
            maxsize=maxsize, ttl=ttl
        )
        self.logger = logger

    def _get_cache_key(
        self, filepath: str, kind: str
    ) -> Tuple[Tuple[str, str], int, int]:
        """Return cache key and file metadata.

        Args:
            filepath (str): File path to inspect.
            kind (str): Cache namespace such as ``"__csv__"``.

        Returns:
            tuple: ``((abs_path, kind), mtime_ns, size)``
        """
        abs_path = os.path.abspath(filepath)
        stat = os.stat(abs_path)
        return (abs_path, kind), stat.st_mtime_ns, stat.st_size

    def clear(self) -> None:
        """Clear the internal cache.

        All cached datasets are removed immediately.
        """
        self.loaded_data.clear()

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """Load ``filepath`` through the in-memory cache.

        The CSV file is read only when its modification time or size differs
        from the cached version.

        Parameters
        ----------
        filepath : str
            CSV file path.
        **kwargs : Any
            Arguments forwarded to :func:`pandas.read_csv`.

        Returns
        -------
        pd.DataFrame
            Cached or newly loaded data.
        """
        key, mtime, size = self._get_cache_key(filepath, "__csv__")
        abs_path = key[0]
        cached = self.loaded_data.get(key)
        if cached:
            if cached.mtime == mtime and cached.size == size:
                if self.logger:
                    self.logger.debug(f"Cache hit: {key}")
                return cached.data

        try:
            kwargs.setdefault("dtype", config.DTYPES)
            df = pd.read_csv(abs_path, **kwargs)
            self.loaded_data[key] = CachedItem(mtime, size, df)
            if self.logger:
                self.logger.info(f"CSV yüklendi: {filepath}")
            return df
        except Exception as e:
            if self.logger:
                self.logger.error(f"CSV yükleme hatası: {filepath}: {e}")
            raise

    def load_excel(self, filepath: str, **kwargs) -> pd.ExcelFile:
        """Load an Excel workbook via the cache.

        The workbook is reloaded whenever its modification time or size
        changes so that updates on disk are reflected immediately.

        Parameters
        ----------
        filepath : str
            Path to the Excel file.
        **kwargs : Any
            Options forwarded to :class:`pandas.ExcelFile`.

        Returns
        -------
        pd.ExcelFile
            Cached or newly loaded workbook instance.
        """
        key, mtime, size = self._get_cache_key(filepath, "__excel__")
        abs_path = key[0]
        cached = self.loaded_data.get(key)
        if cached:
            if cached.mtime == mtime and cached.size == size:
                if self.logger:
                    self.logger.debug(f"Cache hit: {key}")
                return cached.data

        try:
            xls = open_excel_cached(abs_path, **kwargs)
            self.loaded_data[key] = CachedItem(mtime, size, xls)
            if self.logger:
                self.logger.info(f"ExcelFile yüklendi: {filepath}")
            return xls
        except Exception as e:
            if self.logger:
                self.logger.error(f"ExcelFile yükleme hatası: {filepath}: {e}")
            raise
