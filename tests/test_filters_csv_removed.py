import textwrap
from pathlib import Path

import pytest

from backtest import cli
from backtest.config import load_config


def _write_cfg(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "cfg.yml"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def test_cli_filters_args_rejected():
    bad = "--" + "filters"
    msg = (
        "CSV-based or --filters-off flags are removed. "
        "Use --filters-module/--filters-include."
    )
    with pytest.raises(RuntimeError, match=msg):
        cli.main(["scan-day", bad, "foo.csv"])

    bad_off = bad + "-off"
    with pytest.raises(RuntimeError, match=msg):
        cli.main(["scan-day", bad_off])


def test_filters_csv_fields_rejected(tmp_path: Path):
    cfg = _write_cfg(
        tmp_path,
        """
        data:
          filters_csv: foo.csv
        filters:
          module: io_filters
        """,
    )
    with pytest.raises(ValueError, match="CSV-based filters are removed. Use `filters.module`."):
        load_config(cfg)

    cfg = _write_cfg(tmp_path, "filters_csv: foo.csv")
    with pytest.raises(ValueError, match="CSV-based filters are removed. Use `filters.module`."):
        load_config(cfg)

    cfg = _write_cfg(
        tmp_path,
        """
        filters:
          path: foo.csv
        """,
    )
    with pytest.raises(ValueError, match="CSV-based filters are removed. Use `filters.module`."):
        load_config(cfg)


def test_filters_module_missing(tmp_path: Path):
    cfg = _write_cfg(tmp_path, "")
    with pytest.raises(ValueError, match=r"filters.module is required \(default: io_filters\)"):
        load_config(cfg)
