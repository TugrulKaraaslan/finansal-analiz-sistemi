from backtest.downloader.core import DataDownloader
from backtest.downloader.providers.stub import StubProvider


def test_golden_stub(tmp_path):
    prov = StubProvider()
    dl = DataDownloader(prov, data_dir=tmp_path / "out", manifest_path=tmp_path / "manifest.json")
    dl.fetch_range(["DEMO"], "2024-01-01", "2024-01-03")
    report = dl.integrity_check(["DEMO"])
    assert report["DEMO"]["issues"] == []
