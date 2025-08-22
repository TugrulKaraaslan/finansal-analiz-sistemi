from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from .benchmark import load_benchmark


def load_signals_glob(out_dir: str | Path) -> pd.DataFrame:
    root = Path(out_dir)
    rows = []
    for p in sorted(root.glob("*.csv")):
        try:
            df = pd.read_csv(p)
            if {"date", "symbol", "filter_code"}.issubset(df.columns):
                rows.append(df)
        except Exception:
            continue
    if not rows:
        raise FileNotFoundError("SM003: sinyal dosyası yok")
    all_df = pd.concat(rows, ignore_index=True)
    all_df["date"] = pd.to_datetime(all_df["date"]).dt.tz_localize(None)
    return all_df


def _panel_close(df: pd.DataFrame, symbol: str | None = None) -> pd.Series:
    # MultiIndex kolon (symbol, field) ya da tek seviye
    if isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2:
        if symbol is None:
            raise ValueError("symbol None fakat panel MultiIndex")
        return df[(symbol, "close")].astype(float)
    else:
        return df["close"].astype(float)


def _ret(series: pd.Series, horizon: int = 1) -> pd.Series:
    return series.pct_change(periods=horizon).shift(-horizon)


def summarize_day(
    df_prices: pd.DataFrame,
    signals_day: pd.DataFrame,
    bench: pd.Series,
    *,
    horizon: int = 1,
) -> dict:
    day = pd.to_datetime(signals_day["date"].iloc[0]).normalize()
    # Borsa getirisi
    b = (
        bench.reindex(df_prices.index)
        .pct_change(periods=horizon)
        .shift(-horizon)  # noqa: E501
    )
    bist_ret = b.loc[day] if day in b.index else np.nan

    if signals_day.empty:
        return {
            "date": day.date(),
            "signals": 0,
            "filters": 0,
            "coverage": 0,
            "ew_ret": np.nan,
            "bist_ret": bist_ret,
            "alpha": np.nan,
        }

    # sembol listesi
    symbols = sorted(signals_day["symbol"].unique().tolist())
    rets = []
    cov = 0
    for sym in symbols:
        try:
            s_close = _panel_close(
                df_prices,
                sym if isinstance(df_prices.columns, pd.MultiIndex) else None,
            )
        except Exception:
            continue
        r = _ret(s_close, horizon=horizon)
        if day in r.index and pd.notna(r.loc[day]):
            rets.append(r.loc[day])
            cov += 1
    ew_ret = float(np.mean(rets)) if rets else np.nan
    alpha = (
        ew_ret - float(bist_ret)
        if pd.notna(ew_ret) and pd.notna(bist_ret)
        else np.nan  # noqa: E501
    )

    counts = signals_day.groupby("filter_code").size()
    return {
        "date": day.date(),
        "signals": int(len(signals_day)),
        "filters": int(len(counts)),
        "coverage": int(cov),
        "ew_ret": ew_ret,
        "bist_ret": float(bist_ret) if pd.notna(bist_ret) else np.nan,
        "alpha": alpha,
    }


def summarize_range(
    df_prices: pd.DataFrame,
    out_dir: str | Path,
    bench_path: str,
    *,
    horizon: int = 1,
    write_dir: str | Path = "raporlar/ozet",
) -> dict:
    bench = load_benchmark(bench_path)
    all_signals = load_signals_glob(out_dir)
    days = sorted(all_signals["date"].unique())

    daily_rows = []
    filter_rows = []
    for d in days:
        day_df = all_signals[all_signals["date"] == d]
        daily_rows.append(
            summarize_day(df_prices, day_df, bench, horizon=horizon)
        )  # noqa: E501
        # filter counts
        fc = day_df.groupby("filter_code").size().reset_index(name="count")
        fc.insert(0, "date", pd.to_datetime(d).date())
        filter_rows.append(fc)

    daily = pd.DataFrame(daily_rows)
    filter_counts = (
        pd.concat(filter_rows, ignore_index=True)
        if filter_rows
        else pd.DataFrame(columns=["date", "filter_code", "count"])
    )

    write_root = Path(write_dir)
    write_root.mkdir(parents=True, exist_ok=True)
    p1 = write_root / "daily_summary.csv"
    p2 = write_root / "filter_counts.csv"
    daily.to_csv(p1, index=False)
    filter_counts.to_csv(p2, index=False)

    # Kısa markdown
    md = write_root / "summary.md"
    with md.open("w", encoding="utf-8") as f:
        ok = daily.dropna(subset=["alpha"])  # alpha mevcut günler
        if len(ok) > 0:
            mean_alpha = ok["alpha"].mean()
            f.write(
                f"**Gün sayısı:** {len(daily)}  \n"
                f"**Ortalama alpha (H={horizon}):** {mean_alpha:.4%}\n"
            )
        else:
            f.write(
                f"**Gün sayısı:** {len(daily)}  \n"
                "Alpha hesaplanamadı (coverage düşük).\n"
            )

    return {
        "daily_path": str(p1),
        "filter_counts_path": str(p2),
        "markdown_path": str(md),
    }
