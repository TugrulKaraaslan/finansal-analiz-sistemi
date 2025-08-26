import pandas as pd
import pytest

import io_filters
from backtest import cli


def test_io_filters_scan_day_produces_signal(tmp_path, monkeypatch):
    monkeypatch.setattr(
        io_filters,
        "FILTERS",
        [{"FilterCode": "F1", "PythonQuery": "close>0"}],
        raising=False,
    )
    df = pd.DataFrame(
        {
            "Tarih": ["2024-01-02"],
            "Açılış": [10],
            "Yüksek": [10],
            "Düşük": [10],
            "Kapanış": [10],
            "Hacim": [100],
        }
    )
    df.to_excel(tmp_path / "AAA.xlsx", index=False)

    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        f"""
project:
  out_dir: {tmp_path}
  run_mode: range
  start_date: '2024-01-02'
  end_date: '2024-01-02'
  holding_period: 1
  transaction_cost: 0.0
  stop_on_filter_error: false

data:
  excel_dir: {tmp_path}
  enable_cache: false
  price_schema:
    date: ['Tarih']
    open: ['Açılış']
    high: ['Yüksek']
    low: ['Düşük']
    close: ['Kapanış']
    volume: ['Hacim']

filters:
  module: io_filters
  include: ['*']

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

    with pytest.raises(SystemExit) as exc:
        cli.main([
            "scan-day",
            "--config",
            str(cfg_path),
            "--date",
            "2024-01-02",
            "--out",
            str(tmp_path),
        ])
    assert exc.value.code == 0
    out_csv = tmp_path / "2024-01-02.csv"
    assert out_csv.exists()
    rows = pd.read_csv(out_csv)
    assert not rows.empty
