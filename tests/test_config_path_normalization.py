import textwrap
from pathlib import Path

from pathlib import Path
import textwrap

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
        benchmark:
          csv_path: bmk.csv
        """,
    )
    (tmp_path / "data").mkdir()
    (tmp_path / "bmk.csv").write_text("", encoding="utf-8")
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(tmp_path / "data")
    assert cfg.benchmark.csv_path == str(tmp_path / "bmk.csv")


def test_normalize_home(tmp_path: Path, monkeypatch) -> None:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    cfg_file = _write_cfg(
        tmp_path,
        """
        data:
          excel_dir: ~/data
        benchmark:
          csv_path: ~/bmk.csv
        """,
    )
    (home / "data").mkdir()
    (home / "bmk.csv").write_text("", encoding="utf-8")
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(home / "data")
    assert cfg.benchmark.csv_path == str(home / "bmk.csv")


def test_normalize_absolute(tmp_path: Path) -> None:
    abs_data = (tmp_path / "abs_data").resolve()
    abs_data.mkdir()
    abs_bmk = (tmp_path / "abs_bmk.csv").resolve()
    abs_bmk.write_text("", encoding="utf-8")
    cfg_file = _write_cfg(
        tmp_path,
        f"""
        data:
          excel_dir: {abs_data.as_posix()}
        benchmark:
          csv_path: {abs_bmk.as_posix()}
        """,
    )
    cfg = load_config(cfg_file)
    assert cfg.data.excel_dir == str(abs_data)
    assert cfg.benchmark.csv_path == str(abs_bmk)
