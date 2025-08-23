import pandas as pd

from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.local_csv import LocalCSVProvider


def test_fetch_range_local_csv(tmp_path):
    data_dir = tmp_path / "csv"
    data_dir.mkdir()
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "open": [1, 2],
            "high": [1, 2],
            "low": [1, 2],
            "close": [1, 2],
            "volume": [10, 20],
            "quantity": [5, 6],
        }
    )
    df.to_csv(data_dir / "DEMO.csv", index=False)

    prov = LocalCSVProvider(data_dir)
    dl = DataDownloader(prov, data_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json")
    dl.fetch_range(["DEMO"], "2024-01-01", "2024-01-02")

    out = pd.read_parquet(tmp_path / "out" / "symbol=DEMO" / "part-202401.parquet")
    assert len(out) == 2
    pd.testing.assert_series_equal(out["open"], df["open"].astype("float64"), check_names=False)
