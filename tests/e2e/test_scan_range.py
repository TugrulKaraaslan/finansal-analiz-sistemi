from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backtest import cli as bt_cli  # noqa: E402
from tests._utils.synth_data import make_price_frame  # noqa: E402


def test_scan_range_creates_alias_report(tmp_path: Path) -> None:
    df = make_price_frame()
    df.to_excel(tmp_path / "Veriler.xlsx", index=False)

    filters_csv = tmp_path / "filters.csv"
    filters_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "expr": [
                "EMA_10 > close",
                "CROSSUP(EMA_10, close)",
                "RSI_14 >= 5",
                "BBM_20_2.0 < BBU_20_2.1",
            ],
            "FilterCode": ["F1", "F2", "F3", "F4"],
            "PythonQuery": [
                "EMA_10 > close",
                "CROSSUP(EMA_10, close)",
                "RSI_14 >= 5",
                "BBM_20_2.0 < BBU_20_2.1",
            ],
        }
    )
    filters_df.to_csv(filters_csv, index=False)

    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text(
        f"""
project:
  out_dir: {tmp_path}
  run_mode: range
  start_date: '2024-01-01'
  end_date: '2024-01-10'
  holding_period: 1
  transaction_cost: 0.0
  stop_on_filter_error: false
data:
  excel_dir: {tmp_path}
  filters_csv: {filters_csv}
  enable_cache: false
  price_schema:
    date: ['date']
    open: ['open']
    high: ['high']
    low: ['low']
    close: ['close']
    volume: ['volume']
calendar:
  tplus1_mode: price
  holidays_source: none
  holidays_csv_path: ''
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
""",
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
            [
                "scan-range",
                "--config",
                str(cfg_path),
                "--no-preflight",
                "--report-alias",
                "--filters-csv",
                str(filters_csv),
                "--reports-dir",
                str(tmp_path),
            ],
        )
    assert result.exit_code == 0, result.stderr
    report_file = tmp_path / "alias_uyumsuzluklar.csv"
    assert report_file.exists()
    report_txt = report_file.read_text()
    assert "BBM_20_2.0" in report_txt and "BBM_20_2" in report_txt
