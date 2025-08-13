import pandas as pd
from click.testing import CliRunner
import textwrap

from backtest import cli


def test_cli_scan_range_integration(tmp_path):
    df = pd.DataFrame(
        {
            "Tarih": ["2024-01-02", "2024-01-03"],
            "Açılış": [10, 11],
            "Yüksek": [10, 11],
            "Düşük": [10, 11],
            "Kapanış": [10, 11],
            "Hacim": [100, 110],
        }
    )
    df.to_excel(tmp_path / "AAA.xlsx", index=False)
    filters_csv = tmp_path / "filters.csv"
    filters_csv.write_text("FilterCode;PythonQuery\nF1;close > 0\n", encoding="utf-8")
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        textwrap.dedent(
            """
            project:
              out_dir: "{out_dir}"
              run_mode: "range"
              start_date: "2024-01-02"
              end_date: "2024-01-02"
              holding_period: 1
              transaction_cost: 0.0

            data:
              excel_dir: "{out_dir}"
              filters_csv: "{filters}"
              enable_cache: false
              cache_parquet_path: "{out_dir}/cache.parquet"
              price_schema:
                date: ["Tarih"]
                open: ["Açılış"]
                high: ["Yüksek"]
                low: ["Düşük"]
                close: ["Kapanış"]
                volume: ["Hacim"]

            calendar:
              tplus1_mode: "price"
              holidays_source: "none"
              holidays_csv_path: ""

            indicators:
              engine: "builtin"
              params: {{}}

            benchmark:
              xu100_source: "none"
              xu100_csv_path: ""

            report:
              percent_format: "0.00%"
              daily_sheet_prefix: "SCAN_"
              summary_sheet_name: "SUMMARY"
            """
        ).format(out_dir=tmp_path, filters=filters_csv),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(cli.scan_range, ["--config", str(cfg_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "SCAN_2024-01-02.xlsx").exists()


def test_cli_scan_missing_column(tmp_path):
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
    filters_csv = tmp_path / "filters.csv"
    filters_csv.write_text(
        "FilterCode;PythonQuery\nF1;nonexistent > 0\n",
        encoding="utf-8",
    )
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        textwrap.dedent(
            """
            project:
              out_dir: "{out_dir}"
              run_mode: "range"
              start_date: "2024-01-02"
              end_date: "2024-01-02"
              holding_period: 1
              transaction_cost: 0.0

            data:
              excel_dir: "{out_dir}"
              filters_csv: "{filters}"
              enable_cache: false
              cache_parquet_path: "{out_dir}/cache.parquet"
              price_schema:
                date: ["Tarih"]
                open: ["Açılış"]
                high: ["Yüksek"]
                low: ["Düşük"]
                close: ["Kapanış"]
                volume: ["Hacim"]

            calendar:
              tplus1_mode: "price"
              holidays_source: "none"
              holidays_csv_path: ""

            indicators:
              engine: "builtin"
              params: {{}}

            benchmark:
              xu100_source: "none"
              xu100_csv_path: ""

            report:
              percent_format: "0.00%"
              daily_sheet_prefix: "SCAN_"
              summary_sheet_name: "SUMMARY"
            """
        ).format(out_dir=tmp_path, filters=filters_csv),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(cli.scan_range, ["--config", str(cfg_path)])
    assert result.exit_code != 0
    assert isinstance(result.exception, ValueError)
    assert "missing columns" in str(result.exception)
