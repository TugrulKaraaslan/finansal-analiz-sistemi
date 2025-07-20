"""Unit tests for parquet_cache."""

from pathlib import Path

import pandas as pd
import pytest

from finansal.parquet_cache import ParquetCacheManager

pytest.importorskip("pyarrow")


def test_refresh_and_load(tmp_path: Path) -> None:
    """Refresh cache from CSV and ensure subsequent loads match."""
    csv_path = tmp_path / "sample.csv"
    cache_path = tmp_path / "cache.parquet"

    # prepare sample csv
    df_in = pd.DataFrame({"x": [1, 2, 3]})
    df_in.to_csv(csv_path, index=False)

    mngr = ParquetCacheManager(cache_path)
    df_cached = mngr.refresh(csv_path)
    assert len(df_cached) == 3

    df_loaded = mngr.load()
    pd.testing.assert_frame_equal(df_cached, df_loaded)


def test_load_missing(tmp_path: Path) -> None:
    """Raise ``FileNotFoundError`` when the Parquet file is missing."""
    mngr = ParquetCacheManager(tmp_path / "missing.parquet")
    with pytest.raises(FileNotFoundError):
        _ = mngr.load()


def test_exists(tmp_path: Path) -> None:
    """exists should reflect the file system state."""
    cache_path = tmp_path / "cache.parquet"
    mngr = ParquetCacheManager(cache_path)
    assert mngr.exists() is False
    pd.DataFrame({"x": [1]}).to_parquet(cache_path)
    assert mngr.exists() is True
