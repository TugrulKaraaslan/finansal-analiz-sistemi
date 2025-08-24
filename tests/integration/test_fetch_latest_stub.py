from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_fetch_latest_stub(tmp_path):
    prov = StubProvider()
    dl = DataDownloader(prov, data_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json")
    dl.fetch_range(["AAA"], "2024-01-01", "2024-01-03")
    assert dl._manifest["AAA"]["last_date"] == "2024-01-03"
    prev_calls = len(prov.calls)
    dl.fetch_latest(["AAA"], ttl_hours=0)
    assert len(prov.calls) == prev_calls + 1
    assert dl._manifest["AAA"]["last_date"] >= "2024-01-03"
