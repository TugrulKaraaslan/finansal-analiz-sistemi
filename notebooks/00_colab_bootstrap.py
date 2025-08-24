import os
import subprocess
import sys
import tempfile
import textwrap
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    log_dir = PROJECT_ROOT / "loglar"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "colab_bootstrap.log"
    env = {**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"=== {datetime.now().isoformat()} ===\n")
        subprocess.run(
            ["make", "colab-setup"],
            check=True,
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            env=env,
        )
        import pandas as pd

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            df = pd.DataFrame(
                {
                    "date": ["2024-01-01"],
                    "open": [1],
                    "high": [1],
                    "low": [1],
                    "close": [1],
                    "volume": [1],
                    "EMA_10": [1],
                    "RSI_14": [1],
                    "relative_volume": [1],
                    "BBM_20_2.0": [1],
                    "BBU_20_2.1": [1],
                }
            )
            df.to_excel(tmp_path / "AAA.xlsx", index=False)
            filters_csv = tmp_path / "filters.csv"
            filters_csv.write_text("FilterCode;PythonQuery\nF1;close > 0\n", encoding="utf-8")
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
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "backtest.cli",
                    "scan-range",
                    "--config",
                    str(cfg_path),
                    "--no-preflight",
                ],
                check=True,
                cwd=PROJECT_ROOT,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
    print("Kurulum tamamlandı, bir sonraki hücreye geçin")


if __name__ == "__main__":
    main()
