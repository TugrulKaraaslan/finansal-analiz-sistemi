import textwrap
from pathlib import Path

import pytest

from backtest import cli


def test_csv_filters_param_and_field_rejected(tmp_path: Path):
    bad = "--" + "filters"
    with pytest.raises(RuntimeError):
        cli.main(["scan-day", bad, "foo.csv"])

    bad_off = bad + "-off"
    with pytest.raises(RuntimeError):
        cli.main(["scan-day", bad_off])

    cfg = tmp_path / "cfg.yml"
    cfg.write_text(
        textwrap.dedent(
            """
            project:
              out_dir: out
              run_mode: range
              start_date: '2024-01-01'
              end_date: '2024-01-01'
              holding_period: 1
              transaction_cost: 0
            data:
              excel_dir: .
              filters_csv: foo.csv
            filters:
              module: io_filters
              include: ['*']
            """
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        cli.main(["scan-day", "--config", str(cfg), "--date", "2024-01-01"])
