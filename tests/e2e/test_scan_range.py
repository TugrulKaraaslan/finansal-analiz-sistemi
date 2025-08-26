from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import warnings
from click.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backtest import cli as bt_cli  # noqa: E402
from backtest.backtester import run_1g_returns  # noqa: E402
from tests._utils.synth_data import make_price_frame  # noqa: E402
from tests.utils.tmp_filter_module import write_tmp_filters_module  # noqa: E402


def test_scan_range_creates_alias_report(tmp_path: Path) -> None:
    df = make_price_frame()
    df.to_excel(tmp_path / "Veriler.xlsx", index=False)

    mod = write_tmp_filters_module(
        tmp_path,
        [
            {"FilterCode": "F1", "PythonQuery": "EMA_10 > close"},
            {"FilterCode": "F2", "PythonQuery": "CROSSUP(EMA_10, close)"},
            {"FilterCode": "F3", "PythonQuery": "RSI_14 >= 5"},
            {"FilterCode": "F4", "PythonQuery": "BBM_20_2.0 < BBU_20_2.1"},
        ],
    )

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
filters:
  module: {mod}
  include: ["*"]
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

    runner = CliRunner()
    result = runner.invoke(
        bt_cli.cli,
        [
            "scan-range",
            "--config",
            str(cfg_path),
            "--no-preflight",
        ],
    )
    assert result.exit_code == 0, result.stderr


def test_run_1g_returns_empty_no_futurewarning() -> None:
    base = pd.DataFrame(
        {
            "symbol": ["AAA"],
            "date": pd.to_datetime(["2024-01-01"]),
            "close": [1.0],
            "next_date": pd.to_datetime(["2024-01-02"]),
            "next_close": [1.1],
        }
    )
    signals = pd.DataFrame(columns=["FilterCode", "Symbol", "Date"])
    with warnings.catch_warnings(record=True) as w:
        out = run_1g_returns(base, signals)
    assert out.empty
    assert not any(issubclass(w.category, FutureWarning) for w in w)
