import textwrap

import pandas as pd
from click.testing import CliRunner

from backtest import cli


def _write_cfg(tmp_path, filters_path):
    cfg_path = tmp_path / "cfg.yml"
    cfg_path.write_text(
        textwrap.dedent(
            f"""
            project:
              out_dir: {str(tmp_path)}
              run_mode: range
              start_date: '2024-01-01'
              end_date: '2024-01-01'
              holding_period: 1
              transaction_cost: 0.0
            data:
              excel_dir: {str(tmp_path)}
              filters_csv: {str(filters_path)}
              enable_cache: false
            calendar:
              tplus1_mode: price
            indicators:
              engine: none
              params: {{}}
            benchmark:
              source: none
            report:
              percent_format: '0.00%'
              daily_sheet_prefix: 'SCAN_'
              summary_sheet_name: 'SUMMARY'
            """,
        ),
        encoding="utf-8",
    )
    return cfg_path


def test_filters_csv_cli_overrides_yaml(tmp_path):
    df = pd.DataFrame(
        {
            "Tarih": ["2024-01-01"],
            "Açılış": [10],
            "Yüksek": [10],
            "Düşük": [10],
            "Kapanış": [10],
            "Hacim": [100],
        }
    )
    df.to_excel(tmp_path / "AAA.xlsx", index=False)
    filters_yaml = tmp_path / "yaml.csv"
    filters_yaml.write_text(
        "FilterCode;PythonQuery\nF1;close > 0\n", encoding="utf-8")
    filters_cli = tmp_path / "cli.csv"
    filters_cli.write_text(
        "FilterCode;PythonQuery\nF2;close > 0\n", encoding="utf-8")

    cfg_yaml = _write_cfg(tmp_path, filters_yaml)
    runner = CliRunner()
    res_yaml = runner.invoke(
        cli.scan_range, ["--config", str(cfg_yaml), "--no-preflight"]
    )
    assert res_yaml.exit_code == 0, res_yaml.output

    cfg_bad = _write_cfg(tmp_path, tmp_path / "missing.csv")
    res_cli = runner.invoke(
        cli.scan_range,
        [
            "--config",
            str(cfg_bad),
            "--no-preflight",
            "--filters-csv",
            str(filters_cli),
        ],
    )
    assert res_cli.exit_code == 0, res_cli.output
