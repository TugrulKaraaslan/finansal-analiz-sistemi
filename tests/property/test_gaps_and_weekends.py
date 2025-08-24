import pandas as pd

from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_gaps_and_weekends(tmp_path):
    out_dir = tmp_path / "out" / "symbol=AAA"
    out_dir.mkdir(parents=True)
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-06"]),
            "open": [1, 1, 1],
            "high": [1, 1, 1],
            "low": [1, 1, 1],
            "close": [1, 1, 1],
            "volume": [1, 1, 1],
            "quantity": [1, 1, 1],
        }
    )
    df.to_parquet(out_dir / "part-202401.parquet", index=False)
    dl = DataDownloader(
        StubProvider(), data_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json"
    )
    report = dl.integrity_check(["AAA"])
    issues = report["AAA"]["issues"]
    assert "gaps" in issues
    assert "weekend" in issues
