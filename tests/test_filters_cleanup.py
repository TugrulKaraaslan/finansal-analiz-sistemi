import io
from types import SimpleNamespace

import pandas as pd
from click.testing import CliRunner

from backtest import cli
from backtest.filters_cleanup import clean_filters


import pytest


@pytest.fixture
def sample_filters_csv() -> pd.DataFrame:
    csv_str = (
        "id,expr\n"
        "1,CCI_20_0 > 0\n"
        "2,PSARl_0 < close\n"
        "3,BBM_20_2 CROSSUP close\n"
        "4,BBU_20_2 > BBM_20_2\n"
        "5,change_1h_percent > 0\n"
    )
    return pd.read_csv(io.StringIO(csv_str))


def _cfg(tmp_path):
    return SimpleNamespace(
        project=SimpleNamespace(
            out_dir=str(tmp_path),
            start_date=None,
            end_date=None,
            holding_period=1,
            transaction_cost=0.0,
            raise_on_error=False,
        ),
        data=SimpleNamespace(
            filters_csv="dummy.csv",
            excel_dir=".",
            filename_pattern="{date}.xlsx",
            date_format="%Y-%m-%d",
            case_sensitive=True,
        ),
        calendar=SimpleNamespace(
            tplus1_mode="price", holidays_source="none", holidays_csv_path=None
        ),
        indicators=SimpleNamespace(params={}, engine="none"),
        benchmark=SimpleNamespace(
            source="none",
            excel_path="",
            excel_sheet="BIST",
            csv_path="",
            column_date="date",
            column_close="close",
        ),
        report=SimpleNamespace(
            daily_sheet_prefix="SCAN_",
            summary_sheet_name="SUMMARY",
            percent_format="0.00%",
        ),
    )


def test_intraday_cleanup(sample_filters_csv):
    df_clean, report = clean_filters(sample_filters_csv)
    assert 5 not in df_clean["id"].values
    assert report[report["status"] == "intraday_removed"].shape[0] == 1


def test_alias_conversion(sample_filters_csv):
    df_clean, _ = clean_filters(sample_filters_csv)
    assert (
        df_clean.loc[df_clean["id"] == 1, "expr"].iloc[0]
        == "CCI_20_0.015 > 0"
    )
    assert (
        df_clean.loc[df_clean["id"] == 2, "expr"].iloc[0]
        == "PSARl_0.02_0.2 < close"
    )
    assert (
        df_clean.loc[df_clean["id"] == 3, "expr"].iloc[0]
        == "BBM_20_2 CROSSUP close"
    )
    assert (
        df_clean.loc[df_clean["id"] == 4, "expr"].iloc[0]
        == "BBU_20_2 > BBM_20_2"
    )


def test_reporting(sample_filters_csv):
    _, report = clean_filters(sample_filters_csv)
    aliased = report[report["status"] == "aliased"]
    assert set(aliased["original"]) == {"CCI_20_0", "PSARl_0"}
    assert set(aliased["new_symbol"]) == {"CCI_20_0.015", "PSARl_0.02_0.2"}
    intraday = report[report["status"] == "intraday_removed"]
    assert intraday["id"].tolist() == [5]


def test_cli_reports(tmp_path, monkeypatch, sample_filters_csv):
    filters_path = tmp_path / "filters.csv"
    sample_filters_csv.to_csv(filters_path, index=False)
    cfg = _cfg(tmp_path)
    cfg.data.filters_csv = str(filters_path)
    monkeypatch.setattr(cli, "load_config", lambda _: cfg)
    monkeypatch.setattr(cli, "_run_scan", lambda *a, **k: None)
    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        [
            "scan-range",
            "--config",
            "dummy.yml",
            "--no-preflight",
            "--report-alias",
            "--filters-path",
            str(filters_path),
            "--reports-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert (tmp_path / "alias_uyumsuzluklar.csv").exists()
    assert (tmp_path / "filters_intraday_disabled.csv").exists()

