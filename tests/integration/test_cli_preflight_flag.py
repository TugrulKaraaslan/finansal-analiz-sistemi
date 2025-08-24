import pandas as pd

import backtest.cli as cli


def test_cli_preflight_flag(monkeypatch, tmp_path):
    df = pd.DataFrame({"close": [1]}, index=pd.to_datetime(["2025-03-07"]))
    monkeypatch.setattr(cli, "read_excels_long", lambda src: df)
    called = {}

    def fake_validate(filters_csv, excel_dir):
        called["preflight"] = True

    monkeypatch.setattr(cli, "preflight_validate_filters", fake_validate)
    monkeypatch.setattr(cli, "run_scan_range", lambda *a, **k: None)
    monkeypatch.setattr(cli, "list_output_files", lambda *a, **k: [])
    args = [
        "scan-range",
        "--config",
        "config/colab_config.yaml",
        "--start",
        "2025-03-07",
        "--end",
        "2025-03-09",
        "--no-preflight",
        "--out",
        str(tmp_path),
    ]
    import pytest

    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    assert exc.value.code == 0
    assert "preflight" not in called
