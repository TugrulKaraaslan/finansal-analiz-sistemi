from datetime import datetime

from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_ttl_skip(tmp_path):
    prov = StubProvider()
    dl = DataDownloader(prov, data_dir=tmp_path / "parquet", manifest_path=tmp_path / "manifest.json")
    now = datetime.utcnow()
    dl._manifest = {
        "AAA": {
            "last_fetch_ts": now.isoformat(),
            "last_date": "2024-01-05",
            "source": "stub",
            "ttl_hours": 10,
        }
    }
    dl._save_manifest()
    dl.fetch_latest(["AAA"], ttl_hours=10)
    assert prov.calls == []
