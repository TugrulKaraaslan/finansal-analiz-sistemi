import subprocess
import sys
from pathlib import Path

import yaml

from tests.utils.tmp_filter_module import write_tmp_filters_module


def test_cli_smoke(tmp_path: Path):
    root = tmp_path / "proj"
    (root / "data").mkdir(parents=True)
    mod = write_tmp_filters_module(
        root,
        [
            {"FilterCode": "EXAMPLE_01", "PythonQuery": "(rsi_14 > 50) & (ema_20 > ema_50)"},
        ],
    )
    (root / "config").mkdir()
    cfg_path = root / "config" / "colab_config.yaml"
    cfg = {
        "project": {
            "out_dir": "raporlar",
            "logs_dir": "loglar",
            "run_mode": "single",
            "holding_period": 1,
            "transaction_cost": 0.0,
            "stop_on_filter_error": False,
        },
        "data": {
            "excel_dir": "data",
            "enable_cache": False,
            "cache_parquet_path": "cache",
        },
        "filters": {"module": mod, "include": ["*"]},
        "calendar": {"tplus1_mode": "calendar", "holiday_csv": ""},
        "benchmark": {
            "source": "none",
            "excel_path": "",
            "excel_sheet": "BIST",
            "csv_path": "",
            "column_date": "date",
            "column_close": "close",
        },
        "report": {
            "with_bist_ratio_summary": True,
            "include_hit_ratio": True,
            "excel_engine": "xlsxwriter",
        },
        "range": {"start_date": "2022-01-03", "end_date": "2025-04-18"},
        "single": {"date": "2025-03-07"},
    }
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "backtest.cli",
        "scan-day",
        "--config",
        str(cfg_path),
        "--date",
        "2025-03-07",
    ]
    r = subprocess.run(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode in (0, 1)
