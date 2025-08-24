from __future__ import annotations

import importlib.util
import logging
import os
import re
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import pandas as pd
from loguru import logger

from backtest.utils import normalize_key
from utils.paths import resolve_path

from .columns import canonical_map, canonicalize


def _first_existing(*paths: Union[str, Path]) -> Optional[Path]:
    for p in paths:
        if not p:
            continue
        try:
            p_res = resolve_path(p)
        except (OSError, TypeError):
            # path is invalid, cannot be resolved, or of unsupported type
            # continue with next candidate instead of raising an exception
            continue
        if p_res.exists():
            return p_res
    return None


def _guess_excel_dir_from_cfg(cfg: Any) -> Optional[Path]:
    if cfg is None:
        return None

    cand = _first_existing(
        getattr(getattr(cfg, "data", None), "excel_dir", None),
        getattr(getattr(cfg, "data", None), "path", None),
        getattr(cfg, "data_path", None),
    )

    if not cand and isinstance(cfg, dict):
        d = cfg.get("data", {})
        cand = _first_existing(d.get("excel_dir"), d.get("path"), cfg.get("data_path"))

    if cand:
        try:
            return resolve_path(cand)
        except OSError:
            return None

    return None


def normalize_columns(
    df: pd.DataFrame,
    price_schema: Optional[Dict[str, Iterable[str] | str]] = None,
) -> tuple[pd.DataFrame, Dict[str, str]]:
    """Add canonical column aliases to *df* and return mapping.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame whose columns may contain Turkish characters or
        different naming conventions.
    price_schema : dict, optional
        Ignored parameter for backward compatibility.

    Returns
    -------
    tuple
        ``(df, colmap)`` where ``colmap`` maps canonical names to original
        column names.
    """

    colmap = canonical_map(df.columns)
    if price_schema:
        for canon, aliases in price_schema.items():
            if isinstance(aliases, str):
                aliases = [aliases]
            canon_can = canonicalize(canon)
            for al in aliases:
                al_can = canonicalize(al)
                for col in df.columns:
                    if canonicalize(col) == al_can:
                        colmap.setdefault(canon_can, col)
                        if canon_can not in df.columns:
                            df[canon_can] = df[col]
                        break
    for canon, orig in colmap.items():
        if canon not in df.columns:
            df[canon] = df[orig]
    return df, colmap


def validate_columns(df: pd.DataFrame, required: Iterable[str]) -> pd.DataFrame:
    """Ensure that ``df`` contains all columns in ``required``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.
    required : Iterable[str]
        Collection of expected column names.

    Returns
    -------
    pandas.DataFrame
        The original DataFrame if validation succeeds.

    Raises
    ------
    ValueError
        If any of the required columns are missing.
    """
    missing = set(required).difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return df


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame column names and handle duplicates.

    The function removes trailing numeric copy suffixes (``.1`` etc.), applies
    alias mappings for known indicator names and drops or renames duplicate
    columns. All transformations are logged at ``INFO`` level.
    """

    rename_map: Dict[str, str] = {}
    for col in df.columns:
        new = re.sub(r"\.\d+$", "", str(col))
        new = re.sub(r"[^0-9A-Za-z_.]+", "_", new).strip("_")
        new = re.sub(r"__+", "_", new)
        upper = new.upper()
        if upper == "CCI_20_0":
            new = "CCI_20"
        elif upper == "PSARL_0":
            new = "PSARL_0_02_0_2"
        elif upper.startswith("BBM_20_2"):
            new = "BBM_20_2"
        elif upper.startswith("BBU_20_2"):
            new = "BBU_20_2"
        elif upper.startswith("AROONU_"):
            new = re.sub(r"AROONU_(\d+)", r"AROON_UP_\1", upper)
        elif upper.startswith("AROOND_"):
            new = re.sub(r"AROOND_(\d+)", r"AROON_DOWN_\1", upper)
        rename_map[col] = new
        if new != col:
            logging.info("Column '%s' renamed to '%s'", col, new)

    df = df.rename(columns=rename_map)

    seen_series: Dict[str, pd.Series] = {}
    i = 0
    while i < df.shape[1]:
        col = df.columns[i]
        if col not in seen_series:
            seen_series[col] = df.iloc[:, i]
            i += 1
            continue
        first_series = seen_series[col]
        curr_series = df.iloc[:, i]
        if first_series.equals(curr_series):
            logging.info("Dropping duplicate column '%s'", col)
            df = df.iloc[:, [j for j in range(df.shape[1]) if j != i]]
            continue
        new_name = f"{col}_alt"
        j = 1
        while new_name in df.columns:
            j += 1
            new_name = f"{col}_alt{j}"
        logging.info("Column '%s' conflicts with existing; renamed to '%s'", col, new_name)
        df = df.rename(columns={df.columns[i]: new_name})
        seen_series[new_name] = df.iloc[:, i]
        i += 1
    return df


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
    adj["factor"] = pd.to_numeric(adj["factor"], errors="coerce")
    if (adj["factor"] <= 0).any() or adj["factor"].isna().any():
        raise ValueError("corporate actions csv contains invalid factor")
    adj["date"] = pd.to_datetime(adj["date"]).dt.normalize()
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    if not price_cols:
        return df
    df = df.sort_values(["symbol", "date"])
    adj = adj.sort_values(["symbol", "date"])
    adj["cum_factor"] = adj.groupby("symbol")["factor"].transform(lambda x: x[::-1].cumprod()[::-1])
    merged = pd.merge_asof(
        df,
        adj[["symbol", "date", "cum_factor"]],
        on="date",
        by="symbol",
        direction="forward",
        allow_exact_matches=False,
    )
    merged["cum_factor"] = merged["cum_factor"].fillna(1.0)
    merged.loc[:, price_cols] = merged.loc[:, price_cols].mul(merged["cum_factor"], axis=0)
    if "volume" in merged.columns:
        merged["volume"] = merged["volume"].div(merged["cum_factor"])
    merged = merged.drop(columns=["cum_factor"])
    # benchmark note: vectorized version ~5x faster on 10k rows vs loop
    return merged


def read_excels_long(
    cfg_or_path: Union[str, Path, Any],
    engine: str = "auto",
    verbose: bool = False,
) -> pd.DataFrame:
    start_all = time.perf_counter()
    price_schema = None
    if isinstance(cfg_or_path, (str, Path)):
        excel_dir = resolve_path(cfg_or_path)
        enable_cache = None
        cache_path = None
    else:
        excel_dir = _guess_excel_dir_from_cfg(cfg_or_path)
        enable_cache = None
        cache_path = None
        data_cfg = getattr(cfg_or_path, "data", None)
        enable_cache = getattr(data_cfg, "enable_cache", None)
        cache_path = getattr(data_cfg, "cache_parquet_path", None)
        price_schema = getattr(data_cfg, "price_schema", None)
        if enable_cache is None and isinstance(cfg_or_path, dict):
            d = cfg_or_path.get("data", {})
            enable_cache = d.get("enable_cache", None)
            cache_path = d.get("cache_parquet_path", cache_path)
            price_schema = d.get("price_schema", price_schema)

    excel_files: List[Path] = []
    if excel_dir and excel_dir.exists():
        excel_files = sorted(p for p in excel_dir.glob("*.xlsx"))
    if enable_cache is not None:
        enable_cache = bool(str(enable_cache).lower() in ("true", "1"))
    if enable_cache is None:
        enable_cache = len(excel_files) > 5
        if enable_cache:
            logger.info("Cache enabled automatically for {} Excel files", len(excel_files))
    if enable_cache and not cache_path:
        cache_path = excel_dir / "cache.parquet" if excel_dir else None

    aggregated_cache: Optional[Path] = None
    cache_dir: Optional[Path] = None
    if enable_cache and cache_path:
        try:
            cache_file = resolve_path(cache_path)
            if cache_file.exists() and cache_file.is_file():
                try:
                    return pd.read_parquet(cache_file)
                except Exception as e:  # engine missing or wrong format
                    logger.warning("Önbellek okunamadı: {} -> {}", cache_path, e)
                    try:
                        return pd.read_pickle(cache_file)
                    except Exception as e2:
                        logger.warning("Önbellek okunamadı: {} -> {}", cache_path, e2)
            aggregated_cache = cache_file if cache_file.suffix else None
            if cache_file and cache_file.is_dir():
                cache_dir = cache_file
        except Exception as e:
            logger.warning("Önbellek okunamadı: {} -> {}", cache_path, e)
    if enable_cache and not cache_dir and excel_dir:
        cache_dir = excel_dir / ".cache"

    if not excel_dir or not excel_dir.exists():
        msg = (
            f"Excel klasörü bulunamadı: {excel_dir}. "
            "Config'te 'data.excel_dir' yolunu kontrol edin "
            "veya '--excel-dir' ile belirtin."
        )
        logger.error(msg)
        raise FileNotFoundError(msg)
    if not excel_files:
        raise RuntimeError(f"'{excel_dir}' altında .xlsx bulunamadı.")

    if engine == "auto":
        if importlib.util.find_spec("openpyxl"):
            engine_to_use = "openpyxl"
        elif importlib.util.find_spec("xlrd"):
            engine_to_use = "xlrd"
        else:
            raise ImportError("Excel okumak için 'openpyxl' veya 'xlrd' paketleri gerekli")
    elif engine == "openpyxl" and not importlib.util.find_spec("openpyxl"):
        if importlib.util.find_spec("xlrd"):
            engine_to_use = "xlrd"
        else:
            raise ImportError("'openpyxl' bulunamadı ve alternatif Excel motoru saptanamadı")
    else:
        engine_to_use = engine

    def _process_file(fpath: Path) -> pd.DataFrame:
        cache_file = None
        if enable_cache and cache_dir:
            cache_file = cache_dir / (fpath.stem + ".parquet")
            try:
                if cache_file.exists() and cache_file.stat().st_mtime >= fpath.stat().st_mtime:
                    t0 = time.perf_counter()
                    df_cached = pd.read_parquet(cache_file)
                    if verbose:
                        logger.info(
                            "Cache'den okundu: {} ({:.2f}s)",
                            cache_file,
                            time.perf_counter() - t0,
                        )
                    return df_cached
            except Exception as e:
                logger.warning("Cache okunamadı: {} -> {}", cache_file, e)

        t0 = time.perf_counter()
        records_local: List[pd.DataFrame] = []
        try:
            with pd.ExcelFile(fpath, engine=engine_to_use) as xls:
                for sheet in xls.sheet_names:
                    try:
                        try:
                            df = xls.parse(
                                sheet_name=sheet,
                                header=0,
                                dtype_backend="numpy_nullable",
                            )
                        except TypeError:
                            df = xls.parse(sheet_name=sheet, header=0)
                        if df is None or df.empty:
                            continue
                        df, _ = normalize_columns(df, price_schema=price_schema)
                        if "date" not in df.columns:
                            df.columns = [normalize_key(c) for c in df.columns]
                        if "date" not in df.columns:
                            if verbose:
                                logger.info("[SKIP] {}:{} 'date' bulunamadı.", fpath, sheet)
                            continue
                        df["date"] = pd.to_datetime(
                            df["date"].astype(str).str[:10],
                            format="%Y-%m-%d",
                            errors="coerce",
                            dayfirst=False,
                        )
                        df = df.dropna(subset=["date"])
                        keep = [
                            c for c in ["open", "high", "low", "close", "volume"] if c in df.columns
                        ]
                        for c in keep:
                            df[c] = pd.to_numeric(df[c], errors="coerce")
                        df = df.dropna(subset=keep)
                        df = df[(df[keep] >= 0).all(axis=1)]
                        df["symbol"] = str(sheet).strip().upper()
                        records_local.append(df.copy())
                    except Exception as e:
                        if verbose:
                            logger.warning("[WARN] Sheet işlenemedi: {}:{} -> {}", fpath, sheet, e)
                        continue
        except Exception as e:
            if verbose:
                logger.warning("[WARN] Excel açılamadı: {} -> {}", fpath, e)
            return pd.DataFrame()
        if not records_local:
            return pd.DataFrame()
        df_out = pd.concat(records_local, ignore_index=True)
        if enable_cache and cache_file is not None:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                df_out.to_parquet(cache_file, index=False)
                logger.info("Parquet'e dönüştürüldü: {}", cache_file)
            except Exception as e:
                logger.warning("Önbelleğe yazılamadı: {} -> {}", cache_file, e)
        if verbose:
            logger.info("Excel'den okundu: {} ({:.2f}s)", fpath, time.perf_counter() - t0)
        return df_out

    max_workers = min(32, os.cpu_count() or 1)
    with ThreadPoolExecutor(max_workers=max_workers) as exc:
        records = list(exc.map(_process_file, excel_files))

    records = [r for r in records if not r.empty]
    if not records:
        warnings.warn("Hiçbir sheet/çalışma sayfasından veri toplanamadı.")
        cols = ["date", "open", "high", "low", "close", "volume", "symbol"]
        return pd.DataFrame(columns=cols)

    full = pd.concat(records, ignore_index=True)
    full = full.sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    full.drop_duplicates(["symbol", "date"], inplace=True)
    if "close" in full.columns:
        full = full.dropna(subset=["close"])

    full, _ = normalize_columns(full)
    full = canonicalize_columns(full)
    validate_columns(full, ["date", "open", "high", "low", "close", "volume", "symbol"])

    if enable_cache and aggregated_cache:
        try:
            aggregated_cache.parent.mkdir(parents=True, exist_ok=True)
            try:
                full.to_parquet(aggregated_cache, index=False)
            except Exception as e:
                logger.warning("Önbelleğe yazılamadı: {} -> {}", aggregated_cache, e)
                try:
                    full.to_pickle(aggregated_cache)
                except Exception as e2:  # pragma: no cover - logging
                    logger.warning("Önbelleğe yazılamadı: {} -> {}", aggregated_cache, e2)
        except Exception as e:  # pragma: no cover - logging
            logger.warning("Önbelleğe yazılamadı: {} -> {}", aggregated_cache, e)

    if verbose:
        logger.info("Toplam süre: {:.2f}s", time.perf_counter() - start_all)
    return full


__all__ = [
    "read_excels_long",
    "normalize_columns",
    "apply_corporate_actions",
    "validate_columns",
    "canonicalize_columns",
]
