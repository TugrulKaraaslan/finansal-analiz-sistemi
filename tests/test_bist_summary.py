from __future__ import annotations

import pandas as pd
import numpy as np

from backtest.reporter import write_reports


def _basic_trades():
    return pd.DataFrame(
        {
            "FilterCode": ["F1", "F1", "F1", "F1", "F2", "F2"],
            "Symbol": ["A", "A", "A", "A", "B", "B"],
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-03",
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "EntryClose": [1, 1, 1, 1, 1, 1],
            "ExitClose": [1, 1, 1, 1, 1, 1],
            "Side": ["long", "long", "long", "long", "long", "long"],
            "ReturnPct": [2.0, -1.0, 3.0, 1.0, 4.0, -2.0],
            "Win": [True, False, True, True, True, False],
            "Reason": [pd.NA] * 6,
        }
    )


def test_summary_contains_bist_columns(tmp_path):
    trades = _basic_trades()
    summary = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    trade_counts = trades.groupby(["FilterCode"])["Symbol"].count()
    summary = summary.assign(TradeCount=trade_counts)
    xu = {
        pd.Timestamp("2024-01-01"): 1.0,
        pd.Timestamp("2024-01-02"): -0.5,
        pd.Timestamp("2024-01-03"): 0.5,
    }
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(trades, trades["Date"].unique(), summary, xu, out_xlsx=out_xlsx)
    df = pd.read_excel(out_xlsx, sheet_name="SUMMARY")
    for col in ["MEAN_RET", "BIST_MEAN_RET", "ALPHA_RET", "HIT_RATIO", "N_TRADES"]:
        assert col in df.columns
        assert df[col].dtype.kind in "fi"


def test_alpha_computation_alignment(tmp_path):
    trades = _basic_trades()
    summary = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    trade_counts = trades.groupby(["FilterCode"])["Symbol"].count()
    summary = summary.assign(TradeCount=trade_counts)
    xu = {
        pd.Timestamp("2024-01-01"): 1.0,
        pd.Timestamp("2024-01-03"): 0.5,
    }  # missing second day
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(trades, trades["Date"].unique(), summary, xu, out_xlsx=out_xlsx)
    df = pd.read_excel(out_xlsx, sheet_name="SUMMARY")
    f1 = df[df["FilterCode"] == "F1"].iloc[0]
    assert np.isclose(f1["BIST_MEAN_RET"], (1.0 + 0.5) / 2)
    assert np.isclose(f1["ALPHA_RET"], f1["MEAN_RET"] - f1["BIST_MEAN_RET"])


def test_optional_bist_ratio_sheet(tmp_path):
    trades = _basic_trades()
    summary = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    trade_counts = trades.groupby(["FilterCode"])["Symbol"].count()
    summary = summary.assign(TradeCount=trade_counts)
    xu = {
        pd.Timestamp("2024-01-01"): 1.0,
        pd.Timestamp("2024-01-02"): -0.5,
        pd.Timestamp("2024-01-03"): 0.5,
    }
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(
        trades,
        trades["Date"].unique(),
        summary,
        xu,
        out_xlsx=out_xlsx,
        with_bist_ratio_summary=True,
    )
    xl = pd.ExcelFile(out_xlsx)
    assert "BIST_RATIO_SUMMARY" in xl.sheet_names
    out_xlsx2 = tmp_path / "out2.xlsx"
    write_reports(
        trades,
        trades["Date"].unique(),
        summary,
        xu,
        out_xlsx=out_xlsx2,
        with_bist_ratio_summary=False,
    )
    xl2 = pd.ExcelFile(out_xlsx2)
    assert "BIST_RATIO_SUMMARY" not in xl2.sheet_names


def test_sorting_and_values(tmp_path):
    trades = _basic_trades()
    summary = (
        trades.groupby(["FilterCode", "Date"])["ReturnPct"]
        .mean()
        .unstack(fill_value=float("nan"))
    )
    trade_counts = trades.groupby(["FilterCode"])["Symbol"].count()
    summary = summary.assign(TradeCount=trade_counts)
    xu = {
        pd.Timestamp("2024-01-01"): 1.0,
        pd.Timestamp("2024-01-02"): -0.5,
        pd.Timestamp("2024-01-03"): 0.5,
    }
    out_xlsx = tmp_path / "out.xlsx"
    write_reports(
        trades,
        trades["Date"].unique(),
        summary,
        xu,
        out_xlsx=out_xlsx,
        with_bist_ratio_summary=True,
    )
    sum_df = pd.read_excel(out_xlsx, sheet_name="SUMMARY")
    ratio_df = pd.read_excel(out_xlsx, sheet_name="BIST_RATIO_SUMMARY")
    assert ratio_df["ALPHA_RET"].is_monotonic_decreasing
    merged = ratio_df.merge(sum_df, on="FilterCode", suffixes=("_r", "_s"))
    assert np.allclose(merged["ALPHA_RET_r"], merged["ALPHA_RET_s"])
    assert np.allclose(merged["MEAN_RET_r"], merged["MEAN_RET_s"])
