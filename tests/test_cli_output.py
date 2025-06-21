from pathlib import Path
from run import run_pipeline


def test_cli_creates_report(tmp_path):
    out = tmp_path / "cli_report.xlsx"
    root = Path(__file__).parent / "smoke_data"
    run_pipeline(
        price_csv=root / "prices.csv",
        filter_def=root / "filters.yml",
        output=out,
    )
    assert out.exists() and out.stat().st_size > 10_000
