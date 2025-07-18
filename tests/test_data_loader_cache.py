import time

import pandas as pd
import pytest

from data_loader_cache import DataLoaderCache
from finansal_analiz_sistemi import config
from src.utils.excel_reader import open_excel_cached

pytest.importorskip("pyarrow")


def test_clear_also_empties_excel_cache(tmp_path):
    path = tmp_path / "a.xlsx"
    pd.DataFrame({"x": [1]}).to_excel(path, index=False)

    cache = DataLoaderCache()
    first = cache.load_excel(str(path))
    # ensure the workbook comes from the cache
    second = open_excel_cached(path)
    assert first is second

    cache.clear()
    new = cache.load_excel(str(path))
    assert new is not first


def test_parquet_caching(tmp_path):
    path = tmp_path / "b.parquet"
    pd.DataFrame({"y": [1, 2]}).to_parquet(path)

    cache = DataLoaderCache()
    first = cache.load_parquet(str(path))
    second = cache.load_parquet(str(path))
    assert first is second


def test_csv_caching(tmp_path):
    """CSV dosyaları yinelenen okumalarda yeniden yüklenmemeli."""
    path = tmp_path / "c.csv"
    pd.DataFrame({"z": [1, 2]}).to_csv(path, index=False)

    cache = DataLoaderCache()
    first = cache.load_csv(str(path))
    second = cache.load_csv(str(path))
    assert first is second


def test_cache_entry_expires(tmp_path):
    path = tmp_path / "d.csv"
    pd.DataFrame({"x": [1]}).to_csv(path, index=False)

    cache = DataLoaderCache(ttl=1)
    first = cache.load_csv(str(path))
    time.sleep(1.1)
    second = cache.load_csv(str(path))
    assert first is not second


def test_missing_file_raises(tmp_path):
    cache = DataLoaderCache()
    with pytest.raises(FileNotFoundError):
        cache.load_csv(tmp_path / "missing.csv")
    with pytest.raises(FileNotFoundError):
        cache.load_excel(tmp_path / "missing.xlsx")
    with pytest.raises(FileNotFoundError):
        cache.load_parquet(tmp_path / "missing.parquet")


def test_load_csv_respects_dtypes(tmp_path):
    path = tmp_path / "e.csv"
    df_in = pd.DataFrame(
        {
            "open": [1.1, 2.2],
            "close": [3.3, 4.4],
            "volume": [5, 6],
        }
    )
    df_in.to_csv(path, index=False)

    cache = DataLoaderCache()
    df_out = cache.load_csv(path)
    assert str(df_out["open"].dtype) == config.DTYPES["open"]
    assert str(df_out["close"].dtype) == config.DTYPES["close"]
    assert str(df_out["volume"].dtype) == config.DTYPES["volume"]
