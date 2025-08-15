from __future__ import annotations

import logging
import warnings
from pathlib import Path

import pandas as pd

from utils.paths import resolve_path


logger = logging.getLogger(__name__)


_DEFAULT_PATH = Path("/content/finansal-analiz-sistemi/data/BIST100.xlsx")
if not _DEFAULT_PATH.exists():
    _DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "BIST100.xlsx"


def _read_csv_any(path: str | Path) -> pd.DataFrame:
    """Read CSV with fallback separator/decimal handling."""
    p = resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV bulunamadı: {p}")
    try:
        df = pd.read_csv(p, encoding="utf-8")
        if df.shape[1] > 1:
            return df
    except Exception:
        pass
    try:
        with p.open("r", encoding="utf-8") as f:
            sample = f.read(2048)
    except Exception as e:  # SPECIFIC EXCEPTIONS
        raise FileNotFoundError(f"CSV okunamadı: {p}") from e
    import csv

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        sep = dialect.delimiter
    except Exception:
        sep = ","
    dec = "," if sep == ";" else "."
    try:
        return pd.read_csv(p, sep=sep, decimal=dec, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"CSV parse edilemedi: {p}") from e


def load_xu100_pct(csv_path: str | Path | None = None) -> pd.Series:
    """Load BIST100 benchmark returns.

    Parameters
    ----------
    csv_path : str | Path | None, optional
        Optional path to the benchmark file.  If not provided the function
        uses a statically defined repository path.

    Returns
    -------
    pd.Series
        Daily percentage returns. Empty on failure.
    """

    path = Path(csv_path) if csv_path is not None else _DEFAULT_PATH
    try:
        if path.suffix.lower() == ".csv":
            df = _read_csv_any(path)
        elif path.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise FileNotFoundError
    except Exception:
        msg = f"BIST benchmark dosyası okunamadı: {path}"
        warnings.warn(msg)
        logger.warning(msg)
        return pd.Series(dtype=float)

    if df.empty or df.shape[1] < 2:
        warnings.warn(f"Boş CSV: {path}")
        logger.warning("Boş CSV: %s", path)
        return pd.Series(dtype=float)

    cols = {c.lower().strip(): c for c in df.columns}
    # alias mapping for benchmark column
    for alias in ["bist", "bist100"]:
        if alias in cols:
            df = df.rename(columns={cols[alias]: "bist"})
            cols = {c.lower().strip(): c for c in df.columns}
            break

    date_col = cols.get("date") or cols.get("tarih") or list(df.columns)[0]
    value_col = "bist" if "bist" in df.columns else None
    if value_col is None:
        cand = (
            "close",
            "kapanış",
            "kapanis",
            "adjclose",
            "adj_close",
            "kapanis_tl",
            "fiyat",
        )
        for k in cand:
            if k in cols:
                value_col = cols[k]
                break
    if value_col is None and len(df.columns) > 1:
        value_col = list(df.columns)[1]
    if value_col is None:
        msg = f"BIST kolon bulunamadı: {path}"
        warnings.warn(msg)
        logger.warning(msg)
        return pd.Series(dtype=float)

    df[date_col] = pd.to_datetime(
        df[date_col], errors="coerce", dayfirst=True
    ).dt.normalize()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[date_col, value_col]).sort_values(date_col)
    pct = df[value_col].pct_change(1) * 100.0
    pct.index = df[date_col]
    return pct
