import pandas as pd
import pytest

from backtest.reporter import write_reports

def _sample_trades():
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    return pd.DataFrame(
        {
            "FilterCode": ["f1", "f1", "f1"],
            "Symbol": ["SYM1", "SYM2", "SYM3"],
            "Date": dates,
            "EntryClose": [10.0, 11.0, 12.0],
            "ExitClose": [11.0, 12.0, 13.0],
            "Side": ["long", "long", "long"],
            "ReturnPct": [10.0, 9.090909, 8.333333],
            "Win": [True, True, False],
            "Reason": [pd.NA, pd.NA, pd.NA],
        }
    )

def test_per_day_creates_files(tmp_path):
    trades = _sample_trades()
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    summary = pd.DataFrame()
    outputs = write_reports(
        trades,
        dates,
        summary,
        out_xlsx=tmp_path,
        per_day_output=True,
    )
    assert len(outputs["excel"]) == 3
    assert len(outputs.get("csv", [])) == 3
    for d in dates:
        assert (tmp_path / f"{d.date()}.xlsx").exists()
        assert (tmp_path / f"{d.date()}.csv").exists()

def test_per_day_empty_day(tmp_path):
    trades = _sample_trades().iloc[:1]
    dates = pd.to_datetime(["2024-01-01", "2024-01-02"])
    summary = pd.DataFrame()
    write_reports(
        trades,
        dates,
        summary,
        out_xlsx=tmp_path,
        per_day_output=True,
    )
    path = tmp_path / "2024-01-02.xlsx"
    assert path.exists()
    df = pd.read_excel(path, sheet_name="SUMMARY")
    assert int(df["N_TRADES"].iloc[0]) == 0

def test_overwrite_policies(tmp_path):
    trades = _sample_trades().iloc[:1]
    dates = pd.to_datetime(["2024-01-01"])
    summary = pd.DataFrame()
    write_reports(
        trades,
        dates,
        summary,
        out_xlsx=tmp_path,
        per_day_output=True,
    )
    with pytest.raises(FileExistsError):
        write_reports(
            trades,
            dates,
            summary,
            out_xlsx=tmp_path,
            per_day_output=True,
            overwrite="fail",
        )
    write_reports(
        trades,
        dates,
        summary,
        out_xlsx=tmp_path,
        per_day_output=True,
        overwrite="timestamp",
    )
    files = list(tmp_path.glob("*.xlsx"))
    assert len(files) == 2
    assert any("_" in f.stem for f in files)
