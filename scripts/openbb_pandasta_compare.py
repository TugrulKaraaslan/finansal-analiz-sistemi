import numpy as np
import pandas as pd

# Ensure compatibility with pandas-ta on numpy>=2
if not hasattr(np, "NaN"):
    np.NaN = np.nan

import pandas_ta as ta
from openbb_missing import rsi as obb_rsi, macd as obb_macd

INPUT_FILE = "sample_OHLC.csv"
TOL = 1e-6


def compute_indicators_pandasta(df: pd.DataFrame):
    rsi = ta.rsi(df["close"], length=14)
    sma = ta.sma(df["close"], length=14)
    macd_df = ta.macd(df["close"], fast=12, slow=26, signal=9)
    return rsi, sma, macd_df


def compute_indicators_openbb(df: pd.DataFrame):
    results = {}
    errors = {}
    try:
        results["rsi"] = obb_rsi(df["close"], length=14)
    except Exception as e:  # noqa: BLE001
        errors["rsi"] = str(e)
    try:
        # openbb_missing has no SMA wrapper, use pandas to replicate
        results["sma"] = df["close"].rolling(14).mean()
    except Exception as e:  # noqa: BLE001
        errors["sma"] = str(e)
    try:
        results["macd"] = obb_macd(df["close"], fast=12, slow=26, signal=9)
    except Exception as e:  # noqa: BLE001
        errors["macd"] = str(e)
    return results, errors


def main():
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"]).set_index("date")
    p_rsi, p_sma, p_macd = compute_indicators_pandasta(df)
    o_res, errors = compute_indicators_openbb(df)

    report_lines = []
    for key, p_val in {"rsi": p_rsi, "sma": p_sma, "macd": p_macd}.items():
        if key in o_res:
            o_val = o_res[key]
            equal = np.allclose(p_val.values, o_val.values, equal_nan=True, atol=TOL)
            diff = (p_val - o_val).abs().max()
            report_lines.append(f"{key}: match={equal}, max_diff={diff}\n")
        else:
            report_lines.append(f"{key}: openbb error {errors.get(key, 'unknown')}\n")

    report_path = "raporlar/openbb_vs_pandasta.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(report_lines)

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
