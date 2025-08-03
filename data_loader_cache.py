"""
In-memory cache for CSV and Excel files.

Entries are keyed by absolute path and file metadata so repeated reads
avoid disk access. Each cached dataset expires after ``ttl`` seconds.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar, cast

import pandas as pd
from cachetools import TTLCache
from finansal_analiz_sistemi import config

from src.utils.excel_reader import clear_cache as clear_excel_cache
from src.utils.excel_reader import open_excel_cached

T = TypeVar("T")


@dataclass(frozen=True)
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

    def __init__(
        self,
        logger: logging.Logger | None = None,
        *,
        ttl: int = 4 * 60 * 60,
        maxsize: int = 64,
    ) -> None:
        """Initialize the cache and set expiration policy.

        Parameters
        ----------
        logger : logging.Logger, optional
            Logger used for debug messages. When omitted, a module-level
            logger is created automatically.
        ttl : int, optional
            Entry lifetime in seconds.
        maxsize : int, optional
            Maximum number of cached datasets.
        """
        self.loaded_data: TTLCache[tuple[str, str], CachedItem] = TTLCache(
            maxsize=maxsize,
            ttl=ttl,
        )
        self.logger = logger or logging.getLogger(__name__)

    def _get_cache_key(
        self, filepath: str | os.PathLike[str], kind: str
    ) -> tuple[tuple[str, str], int, int]:
        """Return cache key and file metadata for ``filepath``.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            File path to inspect.
        kind : str
            Cache namespace such as ``"__csv__"``.

        Returns
        -------
        tuple
            ``((abs_path, kind), mtime_ns, size)`` describing the file.

        Raises
        ------
        FileNotFoundError
            If ``filepath`` does not exist.
        """
        abs_path = Path(os.fspath(filepath)).expanduser().resolve()
        try:
            stat = abs_path.stat()
        except FileNotFoundError:
            raise FileNotFoundError(str(abs_path))
        return (str(abs_path), kind), stat.st_mtime_ns, stat.st_size

    def clear(self) -> None:
        """Clear all cached datasets and Excel workbooks."""
        for item in self.loaded_data.values():
            data = item.data
            if isinstance(data, pd.ExcelFile):
                try:
                    data.close()
                except Exception as exc:  # pragma: no cover - best effort cleanup
                    if self.logger:
                        self.logger.warning("Excel dosyası kapatılamadı: %s", exc)

        self.loaded_data.clear()
        clear_excel_cache()

    def _load_file(
        self,
        filepath: str | os.PathLike[str],
        *,
        kind: str,
        loader: Callable[[str], T],
    ) -> T:
        """Return cached data loaded via ``loader``.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            File path to load and monitor.
        kind : str
            Cache namespace such as ``"__csv__"``.
        loader : Callable[[str], T]
            Function invoked with the absolute path when a refresh is needed.

        Returns
        -------
        T
            Loaded object either retrieved from the cache or freshly read.
        """

        key, mtime, size = self._get_cache_key(filepath, kind)
        abs_path = key[0]
        cached = self.loaded_data.get(key)
        if cached and cached.mtime == mtime and cached.size == size:
            if self.logger:
                self.logger.debug(f"Cache hit: {key}")
            return cast(T, cached.data)

        if cached and isinstance(cached.data, pd.ExcelFile):
            try:
                cached.data.close()
            except Exception as exc:  # pragma: no cover - best effort cleanup
                if self.logger:
                    self.logger.warning("Önceki Excel dosyası kapatılamadı: %s", exc)

        try:
            data = loader(abs_path)
            self.loaded_data[key] = CachedItem(mtime, size, data)
            if self.logger:
                label = kind.strip("_").upper()
                self.logger.info(f"{label} yüklendi: {filepath}")
            return data
        except Exception as e:
            if self.logger:
                label = kind.strip("_").upper()
                self.logger.error(f"{label} yükleme hatası: {filepath}: {e}")
            raise

    def load_csv(self, filepath: str | os.PathLike[str], **kwargs) -> pd.DataFrame:
        """Load ``filepath`` through the in-memory cache.

        The CSV file is read only when its modification time or size differs
        from the cached version.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            CSV file path.
        **kwargs : Any
            Arguments forwarded to :func:`pandas.read_csv`.

        Returns
        -------
        pd.DataFrame
            Cached or newly loaded data.
        """
        params = {"dtype": config.DTYPES, **kwargs}

        return self._load_file(
            filepath,
            kind="__csv__",
            loader=lambda p: pd.read_csv(p, **params),
        )

    def load_excel(self, filepath: str | os.PathLike[str], **kwargs) -> pd.ExcelFile:
        """Load an Excel workbook via the cache.

        The workbook is reloaded whenever its modification time or size
        changes so that updates on disk are reflected immediately.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            Path to the Excel file.
        **kwargs : Any
            Options forwarded to :class:`pandas.ExcelFile`.

        Returns
        -------
        pd.ExcelFile
            Cached or newly loaded workbook instance.
        """
        return self._load_file(
            filepath,
            kind="__excel__",
            loader=lambda p: open_excel_cached(p, **kwargs),
        )

    def load_parquet(self, filepath: str | os.PathLike[str], **kwargs) -> pd.DataFrame:
        """Load a Parquet file through the cache.

        Parameters
        ----------
        filepath : str | os.PathLike[str]
            Parquet file path.
        **kwargs : Any
            Arguments forwarded to :func:`pandas.read_parquet`.

        Returns
        -------
        pandas.DataFrame
            Cached or newly loaded DataFrame.
        """
        return self._load_file(
            filepath,
            kind="__parquet__",
            loader=lambda p: pd.read_parquet(p, **kwargs),
        )

    def __del__(self) -> None:  # pragma: no cover - cleanup safeguard
        """Ensure cached workbooks are closed on garbage collection."""
        try:
            self.clear()
        except Exception:
            pass


__all__ = ["DataLoaderCache"]
