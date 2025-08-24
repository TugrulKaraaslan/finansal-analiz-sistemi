import pandas as pd

import backtest.cli as cli


def test_cli_scan_range_smoke(monkeypatch, tmp_path):
    df = pd.DataFrame({"close": [1]}, index=pd.to_datetime(["2025-03-07"]))
    monkeypatch.setattr(cli, "read_excels_long", lambda src: df)

    called = {}

    def fake_run_scan_range(df_arg, start, end, filters_df, out_dir=None, alias_csv=None):
        called["ran"] = True
        assert start == "2025-03-07"
        assert end == "2025-03-09"
        assert not filters_df.empty
        return None

    monkeypatch.setattr(cli, "run_scan_range", fake_run_scan_range)
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
    assert called.get("ran")
