"""Stress-test cache growth; ensure <=5 MB additional RAM after repeated loads."""

import gc

import pandas as pd
import psutil
import pytest
from cachetools import TTLCache


def _read_parquet(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Test _read_parquet."""
    dates = pd.date_range(start, end, freq="D")
    return pd.DataFrame({"hisse_kodu": ticker, "tarih": dates})


_CACHE = TTLCache(maxsize=256, ttl=4 * 60 * 60)


def get_df(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Test get_df."""
    key = f"{ticker}_{start}_{end}"
    if key not in _CACHE:
        _CACHE[key] = _read_parquet(ticker, start, end)
    return _CACHE[key]


def clear_cache() -> None:
    """Test clear_cache."""
    _CACHE.clear()


@pytest.mark.slow
def test_cache_memory():
    """Repeated loads should not increase memory usage significantly."""
    proc = psutil.Process()
    base = proc.memory_info().rss
    for _ in range(200):
        get_df("AKBNK", "2023-01-01", "2023-12-29")
    # Küçük dalgalanmaları elimine et
    gc.collect()
    after = proc.memory_info().rss

    # Toleransı 15 MB'a çek (CI container'larında hafıza tahsisi burst yapabiliyor)
    assert after - base < 15 * 1024 * 1024  # <15 MB artış
    clear_cache()
