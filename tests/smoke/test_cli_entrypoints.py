from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from click.testing import CliRunner
from tests._utils.synth_data import make_price_frame
from backtest import cli as bt_cli


def test_scan_range_help_shows_options() -> None:
    root = Path(__file__).resolve().parents[2]
    env = {**os.environ, "PYTHONPATH": str(root)}
    result = subprocess.run(
        [sys.executable, "-m", "backtest.cli", "scan-range", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert "--report-alias" in result.stdout
    assert "--filters-path" in result.stdout


def test_scan_range_dry_run(tmp_path: Path) -> None:
    df = make_price_frame(1)
    df.to_excel(tmp_path / "AAA.xlsx", index=False)
    filters_csv = tmp_path / "filters.csv"
    pd.DataFrame(
        {
            "id": [1],
            "expr": ["close > 0"],
            "FilterCode": ["F1"],
            "PythonQuery": ["close > 0"],
        }
    ).to_csv(filters_csv, index=False)
    cfg_path = tmp_path / "cfg.yml"
    cfg_path.write_text(
        textwrap.dedent(
            f"""
            project:
              out_dir: {tmp_path}
              run_mode: range
              start_date: '2024-01-01'
              end_date: '2024-01-01'
              holding_period: 1
              transaction_cost: 0.0
              stop_on_filter_error: false
            data:
              excel_dir: {tmp_path}
              filters_csv: {filters_csv}
              enable_cache: false
            calendar:
              tplus1_mode: price
            indicators:
              engine: none
              params: {{}}
            benchmark:
              source: none
              excel_path: ''
              excel_sheet: BIST
              csv_path: ''
              column_date: date
              column_close: close
            report:
              percent_format: '0.00%'
              daily_sheet_prefix: 'SCAN_'
              summary_sheet_name: 'SUMMARY'
            """
        ),
        encoding="utf-8",
    )

    def _compile(src, dst):
        df = pd.read_csv(src, sep=None, engine="python")
        df = df.rename(columns={"id": "FilterCode", "expr": "PythonQuery"})
        df = df[["FilterCode", "PythonQuery"]]
        df.to_csv(dst, sep=";", index=False)

    runner = CliRunner()
    with patch("backtest.cli.compile_filters", _compile):
        result = runner.invoke(
            bt_cli.cli,
            ["scan-range", "--config", str(cfg_path), "--no-preflight"],
        )
    assert result.exit_code == 0
