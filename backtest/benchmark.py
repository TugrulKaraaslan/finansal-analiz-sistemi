from __future__ import annotations
import pandas as pd
import io, csv

def _read_csv_any(path: str) -> pd.DataFrame:
    # Try default, then ; separator, decimal comma
    try:
        return pd.read_csv(path)
    except Exception:
        with open(path, "r", encoding="utf-8") as f:
            sample = f.read(2048)
        sep = ";" if sample.count(";") > sample.count(",") else ","
        dec = "," if sample.count(",") > sample.count(".") and sep == ";" else "."
        return pd.read_csv(path, sep=sep, decimal=dec)

def load_xu100_pct(csv_path: str) -> pd.Series:
    df = _read_csv_any(csv_path)
    cols = {c.lower().strip(): c for c in df.columns}
    # date column
    c_date = cols.get("date") or cols.get("tarih") or list(df.columns)[0]
    # close-like column
    cand = ["close","kapanış","kapanis","adjclose","adj_close","kapanis_tl","fiyat"]
    close_col = None
    for k in cand:
        if k in cols:
            close_col = cols[k]; break
    if close_col is None:
        # fallback: second column
        close_col = list(df.columns)[1]
    # parse date tolerant
    df[c_date] = pd.to_datetime(df[c_date], errors="coerce", dayfirst=True).dt.date
    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")
    df = df.dropna(subset=[c_date, close_col]).sort_values(c_date)
    pct = df[close_col].pct_change(1) * 100.0
    pct.index = df[c_date]
    return pct
