import pandas as pd
from click.testing import CliRunner

from backtest import cli
from backtest.data_loader import canonicalize_columns, read_excels_long


def test_duplicate_columns_collapsed():
    df = pd.DataFrame(
        {
            "BBM_20_2.0": [1, 2, 3],
            "BBM_20_2.1": [1, 2, 3],
        }
    )
    out = canonicalize_columns(df)
    assert "BBM_20_2" in out.columns
    assert list(out.columns).count("BBM_20_2") == 1


def test_alias_columns():
    df = pd.DataFrame(
        {
            "CCI_20_0": [1, 2],
            "PSARl_0": [3, 4],
        }
    )
    out = canonicalize_columns(df)
    assert "CCI_20" in out.columns
    assert "PSARL_0_02_0_2" in out.columns


def test_relative_volume_preserved(tmp_path):
    data = pd.DataFrame(
        {
            "Tarih": ["2024-01-02"],
            "Open": [1.0],
            "High": [1.5],
            "Low": [0.5],
            "Close": [1.2],
            "Volume": [1000],
            "relative_volume": [1.1],
        }
    )
    fpath = tmp_path / "sample.xlsx"
    data.to_excel(fpath, sheet_name="AAA", index=False)
    df = read_excels_long(tmp_path)
    assert "relative_volume" in df.columns


def test_no_preflight_flag(monkeypatch, tmp_path):
    cfg_path = tmp_path / "cfg.yml"
    excel_dir = tmp_path / "data"
    excel_dir.mkdir()
    filters = tmp_path / "filters.csv"
    filters.write_text("FilterCode;PythonQuery\n")
    cfg_path.write_text(
        (
            "project:\n"
            '  start_date: "2024-01-02"\n'
            '  end_date: "2024-01-05"\n'
            f"  out_dir: {tmp_path / 'out'}\n"
            f"data:\n"
            f"  excel_dir: {excel_dir}\n"
            f"  filters_csv: {filters}\n"
        )
    )
    runner = CliRunner()
    monkeypatch.setattr(
        cli,
        "_run_scan",
        lambda *a, **k: None,
    )
    called = {"flag": False}

    def _pf(*a, **k):
        called["flag"] = True

        class Dummy:
            warnings = ["Eksik dosyalar: ..."]
            errors = []
            suggestions = []

        return Dummy()

    monkeypatch.setattr(cli, "preflight", _pf)
    result = runner.invoke(
        cli.scan_range,
        [
            "--config",
            str(cfg_path),
            "--no-preflight",
            "--start",
            "2024-01-02",
            "--end",
            "2024-01-05",
        ],
    )
    assert result.exit_code == 0
    assert "Eksik dosyalar" not in result.output
    assert called["flag"] is False
