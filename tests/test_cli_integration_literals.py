import textwrap
import uuid
from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from backtest import cli


def test_scan_range_bool_literals(tmp_path):
    # Prepare minimal price data
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

    # filters.csv with boolean literals
    csv_path = tmp_path / "filters.csv"
    csv_path.write_text("FilterCode,PythonQuery\nF1,true\nF2,false\n", encoding="utf-8")

    # Module that loads CSV
    mod_name = f"tmp_filters_{uuid.uuid4().hex[:8]}"
    mod_path = Path(tmp_path) / f"{mod_name}.py"
    mod_path.write_text(
        textwrap.dedent(
            f"""
            import pandas as pd

            def get_filters():
                return pd.read_csv(r"{csv_path}").to_dict('records')
            """
        ),
        encoding="utf-8",
    )
    import sys

    if str(tmp_path) not in sys.path:
        sys.path.insert(0, str(tmp_path))

    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        textwrap.dedent(
            f"""
            project:
              out_dir: "{tmp_path}"
              run_mode: "range"
              start_date: "2024-01-02"
              end_date: "2024-01-02"
              holding_period: 1
              transaction_cost: 0.0

            data:
              excel_dir: "{tmp_path}"
              enable_cache: false
              cache_parquet_path: "{tmp_path}/cache.parquet"
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
              engine: "none"
              params: {{}}

            benchmark:
              source: "none"
              excel_path: ""
              excel_sheet: "BIST"
              csv_path: ""
              column_date: "date"
              column_close: "close"

            report:
              percent_format: "0.00%"
              daily_sheet_prefix: "SCAN_"
              summary_sheet_name: "SUMMARY"

            filters:
              module: {mod_name}
              include: ["*"]
            """
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli.scan_range, ["--config", str(cfg_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "SCAN_2024-01-02.xlsx").exists()

