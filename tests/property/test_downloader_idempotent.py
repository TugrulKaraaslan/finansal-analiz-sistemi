import pandas as pd

from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_idempotent_fetch(tmp_path):
    prov = StubProvider()
    dl = DataDownloader(prov, data_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json")
    dl.fetch_range(["AAA"], "2024-01-01", "2024-01-05")
    dl.fetch_range(["AAA"], "2024-01-01", "2024-01-05")
    df = pd.read_parquet(tmp_path / "out" / "symbol=AAA" / "part-202401.parquet")
    assert not df["date"].duplicated().any()
