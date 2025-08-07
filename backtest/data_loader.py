# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from loguru import logger

from backtest.utils import normalize_key
from utils.paths import resolve_path


def _first_existing(*paths: Union[str, Path]) -> Optional[Path]:
    for p in paths:
        if not p:
            continue
        try:
            p_res = resolve_path(p)
        except OSError:
            # path is invalid or cannot be resolved, try next candidate
            continue
        if p_res.exists():
            return p_res
    return None


def _guess_excel_dir_from_cfg(cfg: Any) -> Optional[Path]:
    if cfg is None:
        return None
    try:
        cand = _first_existing(
            getattr(getattr(cfg, "data", None), "excel_dir", None),
            getattr(getattr(cfg, "data", None), "path", None),
            getattr(cfg, "data_path", None),
        )
        if cand:
            return resolve_path(cand)
    except Exception:
        pass
    try:
        d = cfg.get("data", {}) if isinstance(cfg, dict) else {}
        cand = _first_existing(d.get("excel_dir"), d.get("path"), cfg.get("data_path"))
        if cand:
            return resolve_path(cand)
    except Exception:
        pass
    return None


COL_ALIASES: Dict[str, str] = {
    "date": "date",
    "tarih": "date",
    "tarihi": "date",
    "open": "open",
    "acilis": "open",
    "açilis": "open",
    "açilis_fiyati": "open",
    "açilis_fiyati_": "open",
    "high": "high",
    "yuksek": "high",
    "yüksek": "high",
    "low": "low",
    "dusuk": "low",
    "düşük": "low",
    "close": "close",
    "kapanis": "close",
    "kapanış": "close",
    "son": "close",
    "son_fiyat": "close",
    "adj_close": "close",
    "volume": "volume",
    "hacim": "volume",
    "islem_hacmi": "volume",
    "işlem_hacmi": "volume",
    "adet": "volume",
    "lot": "volume",
    "kapanis_fiyati": "close",
    "kapanis_fiyat": "close",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame")  # TİP DÜZELTİLDİ
    rename_map: Dict[str, str] = {}
    for c in df.columns:
        key = normalize_key(c).strip("_")
        std = COL_ALIASES.get(key, key)
        rename_map[c] = std
    result = df.rename(columns=rename_map)
    # renaming may cause different original names to map to the same target
    if result.columns.duplicated().any():
        dup = result.columns[result.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate columns after normalization: {dup}")
    return result


def apply_corporate_actions(
    df: pd.DataFrame, csv_path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """Adjust price data for corporate actions using an adjustment CSV.

    CSV must have columns: ``symbol``, ``date``, ``factor``. Prices prior to
    ``date`` are multiplied by ``factor``.
    """
    if csv_path is None:
        return df
    try:
        path = resolve_path(csv_path)
    except Exception:
        warnings.warn("Corporate actions path cannot be resolved")
        return df
    if not path.exists():
        warnings.warn("Corporate actions file not found")
        return df
    adj = pd.read_csv(path)
    if adj.empty:
        return df
    adj = adj.rename(columns=str.lower)
    if not {"symbol", "date", "factor"}.issubset(adj.columns):
        raise ValueError("corporate actions csv missing required columns")
    adj["date"] = pd.to_datetime(adj["date"]).dt.normalize()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    for sym, grp in adj.groupby("symbol"):
        for _, row in grp.sort_values("date").iterrows():
            mask = (df["symbol"] == sym) & (df["date"] < row["date"])
            df.loc[mask, price_cols] = df.loc[mask, price_cols] * float(row["factor"])
    return df


def read_excels_long(
    cfg_or_path: Union[str, Path, Any],
    dayfirst: bool = True,
    engine: str = "openpyxl",
    verbose: bool = False,
) -> pd.DataFrame:
    if isinstance(cfg_or_path, (str, Path)):
        excel_dir = resolve_path(cfg_or_path)
        enable_cache = None
        cache_path = None
    else:
        excel_dir = _guess_excel_dir_from_cfg(cfg_or_path)
        enable_cache = None
        cache_path = None
        try:
            enable_cache = getattr(
                getattr(cfg_or_path, "data", None), "enable_cache", None
            )
            cache_path = getattr(
                getattr(cfg_or_path, "data", None), "cache_parquet_path", None
            )
        except Exception:
            pass
        if enable_cache is None and isinstance(cfg_or_path, dict):
            d = cfg_or_path.get("data", {})
            enable_cache = d.get("enable_cache", None)
            cache_path = d.get("cache_parquet_path", cache_path)

    excel_files: List[Path] = []
    if excel_dir and excel_dir.exists():
        excel_files = sorted(p for p in excel_dir.glob("*.xlsx"))
    if enable_cache is None:
        enable_cache = len(excel_files) > 5
        if enable_cache:
            logger.info(
                "Cache enabled automatically for %d Excel files", len(excel_files)
            )
    if enable_cache and not cache_path:
        cache_path = excel_dir / "cache.parquet" if excel_dir else None

    if enable_cache and cache_path:
        try:
            cache_file = resolve_path(cache_path)
            if cache_file.exists():
                return pd.read_parquet(cache_file)
        except Exception as e:
            logger.warning("Önbellek okunamadı: %s -> %s", cache_path, e)

    if not excel_dir or not excel_dir.exists():
        raise FileNotFoundError(f"Excel klasörü bulunamadı: {excel_dir}")

    records: List[pd.DataFrame] = []
    if not excel_files:
        raise RuntimeError(f"'{excel_dir}' altında .xlsx bulunamadı.")

    for fpath in excel_files:
        try:
            xls = pd.ExcelFile(fpath, engine=engine)
        except Exception as e:
            if verbose:
                print(f"[WARN] Excel açılamadı: {fpath} -> {e}")
            continue

        for sheet in xls.sheet_names:
            try:
                df = xls.parse(sheet_name=sheet, header=0)
                if df is None or df.empty:
                    continue
                df = normalize_columns(df)
                if "date" not in df.columns:
                    df.columns = [normalize_key(c) for c in df.columns]
                if "date" not in df.columns:
                    if verbose:
                        print(f"[SKIP] {fpath}:{sheet} 'date' bulunamadı.")
                    continue

                df["date"] = pd.to_datetime(
                    df["date"], errors="coerce", dayfirst=dayfirst
                )
                df = df.dropna(subset=["date"])

                keep = [
                    c
                    for c in ["open", "high", "low", "close", "volume"]
                    if c in df.columns
                ]
                df = df[["date", *keep]].copy()
                for c in keep:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

                df["symbol"] = str(sheet).strip().upper()
                records.append(df)
            except Exception as e:
                if verbose:
                    print(f"[WARN] Sheet işlenemedi: {fpath}:{sheet} -> {e}")
                continue

    if not records:
        warnings.warn("Hiçbir sheet/çalışma sayfasından veri toplanamadı.")
        return pd.DataFrame()

    full = pd.concat(records, ignore_index=True)
    full = full.sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    # remove duplicate symbol/date combinations that may appear across sheets/files
    full.drop_duplicates(["symbol", "date"], inplace=True)
    if "close" in full.columns:
        full = full.dropna(subset=["close"])

    if enable_cache and cache_path:
        try:
            cache_file = resolve_path(cache_path)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            full.to_parquet(cache_file, index=False)
        except Exception as e:  # pragma: no cover - logging
            logger.warning("Önbelleğe yazılamadı: %s -> %s", cache_path, e)

    return full


__all__ = ["read_excels_long", "normalize_columns"]
