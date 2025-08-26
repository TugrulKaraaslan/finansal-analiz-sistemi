import textwrap
from pathlib import Path

from backtest.config import load_config


def _write_cfg(tmp_path: Path, content: str) -> Path:
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(textwrap.dedent(content), encoding="utf-8")
    return cfg_file


def test_normalize_relative(tmp_path: Path) -> None:
    cfg_file = _write_cfg(
        tmp_path,
        """
        data:
          excel_dir: data
        filters:
          module: io_filters
        """,
    )
    (tmp_path / "data").mkdir()
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(tmp_path / "data")
    assert cfg.filters.module == "io_filters"


def test_normalize_home(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    cfg_file = _write_cfg(
        tmp_path,
        """
        data:
          excel_dir: ~/data
        filters:
          module: io_filters
        """,
    )
    (home / "data").mkdir()
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(home / "data")


def test_normalize_absolute(tmp_path: Path) -> None:
    abs_data = (tmp_path / "abs_data").resolve()
    abs_data.mkdir()
    cfg_file = _write_cfg(
        tmp_path,
        f"""
        data:
          excel_dir: {abs_data.as_posix()}
        filters:
          module: io_filters
        """,
    )
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(abs_data)
