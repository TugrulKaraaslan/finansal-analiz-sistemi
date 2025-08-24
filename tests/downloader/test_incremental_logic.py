from datetime import date, datetime

from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_next_start_from_manifest(tmp_path):
    prov = StubProvider()
    dl = DataDownloader(
        prov, data_dir=tmp_path / "parquet", manifest_path=tmp_path / "manifest.json"
    )
    dl._manifest = {
        "AAA": {
            "last_fetch_ts": datetime(2024, 1, 5).isoformat(),
            "last_date": "2024-01-05",
            "source": "stub",
            "ttl_hours": 0,
        }
    }
    dl._save_manifest()
    dl.fetch_latest(["AAA"], ttl_hours=0)
    assert prov.calls
    symbol, start, end = prov.calls[0]
    assert start == date(2024, 1, 6)
