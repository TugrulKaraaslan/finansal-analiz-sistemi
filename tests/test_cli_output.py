"""Integration tests for the command-line reporting pipeline.

These tests run a small backtest end-to-end to ensure CSV inputs are
processed correctly and Excel reports are generated.
"""

from pathlib import Path

import pytest

ta = pytest.importorskip("pandas_ta")
if not hasattr(ta, "psar"):
    pytest.skip("psar not available", allow_module_level=True)

from run import run_pipeline  # noqa: E402


def test_cli_creates_report(tmp_path):
    """Running the pipeline should write an Excel report."""
    out = tmp_path / "cli_report.xlsx"
    root = Path(__file__).parent / "smoke_data"
    result = run_pipeline(
        price_csv=root / "prices.csv",
        filter_def=root / "filters.yml",
        output=out,
    )
    assert out.exists() and out.stat().st_size > 10_000
    assert result == out
    assert isinstance(result, Path)
