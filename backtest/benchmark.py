# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

from pathlib import Path
import warnings
import pandas as pd


def _read_csv_any(path: str | Path) -> pd.DataFrame:
    """Read CSV with fallback separator/decimal handling."""
    p = Path(path)
    if not p.exists():  # PATH DÜZENLENDİ
        warnings.warn(f"CSV bulunamadı: {p}")
        return pd.DataFrame()
    try:
        return pd.read_csv(p, encoding="utf-8")  # PATH DÜZENLENDİ
    except Exception:
        try:
            with p.open("r", encoding="utf-8") as f:  # PATH DÜZENLENDİ
                sample = f.read(2048)
        except Exception:
            warnings.warn(f"CSV okunamadı: {p}")  # PATH DÜZENLENDİ
            return pd.DataFrame()
        sep = ";" if sample.count(";") > sample.count(",") else ","
        dec = "," if sample.count(",") > sample.count(".") and sep == ";" else "."
        try:
            return pd.read_csv(p, sep=sep, decimal=dec, encoding="utf-8")  # PATH DÜZENLENDİ
        except Exception:
            warnings.warn(f"CSV parse edilemedi: {p}")  # PATH DÜZENLENDİ
            return pd.DataFrame()


def load_xu100_pct(csv_path: str | Path) -> pd.Series:
    if not isinstance(csv_path, (str, Path)):
        raise TypeError("csv_path must be str or Path")  # TİP DÜZELTİLDİ
    df = _read_csv_any(csv_path)  # PATH DÜZENLENDİ
    if df.empty or df.shape[1] == 0:  # Kolon yoksa list indeksleme taşar
        warnings.warn(f"Boş CSV: {csv_path}")  # PATH DÜZENLENDİ
        return pd.Series(dtype=float)  # LOJİK HATASI DÜZELTİLDİ
    cols = {c.lower().strip(): c for c in df.columns}
    # date column
    c_date = cols.get("date") or cols.get("tarih") or list(df.columns)[0]
    # close-like column
    cand = (
        "close",
        "kapanış",
        "kapanis",
        "adjclose",
        "adj_close",
        "kapanis_tl",
        "fiyat",
    )  # TİP DÜZELTİLDİ
    close_col = None
    for k in cand:
        if k in cols:
            close_col = cols[k]
            break
    if close_col is None:
        # fallback: second column if available
        close_col = (
            list(df.columns)[1] if len(df.columns) > 1 else list(df.columns)[0]
        )  # TİP DÜZELTİLDİ
    # parse date tolerant
    df[c_date] = pd.to_datetime(df[c_date], errors="coerce", dayfirst=True).dt.date
    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")
    df = df.dropna(subset=[c_date, close_col]).sort_values(c_date)
    pct = df[close_col].pct_change(1) * 100.0
    pct.index = df[c_date]
    return pct
