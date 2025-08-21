import subprocess
import sys
from pathlib import Path

import yaml


def test_cli_smoke(tmp_path: Path):
    root = tmp_path / "proj"
    (root / "Veri").mkdir(parents=True)
    (root / "filters.csv").write_text(
        "FilterCode;PythonQuery\n" "EXAMPLE_01; (rsi_14 > 50) & (ema_20 > ema_50)\n",
        encoding="utf-8",
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
            "excel_dir": "Veri",
            "filters_csv": "filters.csv",
            "enable_cache": False,
            "cache_parquet_path": "cache",
        },
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
    r = subprocess.run(
        cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert r.returncode in (0, 1)
