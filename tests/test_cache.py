import pandas as pd

from finansal_analiz_sistemi import cache_builder, config, data_loader


def test_rebuild_creates_nonempty_parquet(tmp_path, monkeypatch):
    csv = tmp_path / "a.csv"
    pd.DataFrame(
        {
            "date": ["2025-01-01"],
            "ticker": ["AAA"],
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [100],
        }
    ).to_csv(csv, index=False)

    monkeypatch.setattr(cache_builder, "RAW_DIR", tmp_path)
    monkeypatch.setattr(cache_builder, "CACHE", tmp_path / "cache.parquet")
    monkeypatch.setattr(
        cache_builder, "LOCK_FILE", cache_builder.CACHE.with_suffix(".lock")
    )
    monkeypatch.setattr(config, "PARQUET_CACHE_PATH", str(cache_builder.CACHE))

    cache_builder.CACHE.unlink(missing_ok=True)
    cache_builder.build()
    df = data_loader.load_dataset()
    assert len(df) > 0
