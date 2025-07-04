# data_loader_cache.py
import os

import pandas as pd
from cachetools import TTLCache

from finansal_analiz_sistemi import config
from src.utils.excel_reader import open_excel_cached

CACHE: TTLCache = TTLCache(maxsize=256, ttl=4 * 60 * 60)  # 4 saat LRU+TTL


class DataLoaderCache:
    """Basit dosya okuma önbelleği.

    Bu sınıf, CSV ve Excel dosyalarının diskten her okunuşunda tekrar
    yüklenmesini önlemek için basit bir bellek içi önbellek tutar. ``load_csv``
    ve ``load_excel`` metodları aynı dosya yolu için daha önce yüklenmiş bir
    nesne varsa bunu döndürür, aksi halde dosyayı okuyup önbelleğe ekler.

    Args:
        logger (logging.Logger, optional): İşlemler hakkında bilgi vermek için
            kullanılacak logger nesnesi.
    """

    def __init__(self, logger=None, *, ttl: int = 4 * 60 * 60, maxsize: int = 64):
        self.loaded_data: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.logger = logger

    def load_excel(self, filepath: str, **kwargs) -> pd.ExcelFile:
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

    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
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

    def clear(self) -> None:
        """Clear the internal cache."""
        self.loaded_data.clear()


def _read_parquet(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Simulate reading parquet data for a ticker between two dates."""

    dates = pd.date_range(start, end, freq="D")
    return pd.DataFrame({"hisse_kodu": ticker, "tarih": dates})


def get_df(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Return cached DataFrame for ``ticker`` between ``start`` and ``end``."""

    key = f"{ticker}_{start}_{end}"
    if key in CACHE:
        return CACHE[key]
    df = _read_parquet(ticker, start, end)
    CACHE[key] = df
    return df


def clear_cache() -> None:
    """Empty the global cache."""

    CACHE.clear()
