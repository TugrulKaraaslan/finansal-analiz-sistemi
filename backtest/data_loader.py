import re
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

_TR_MAP = str.maketrans({
    "İ": "I", "I": "I",
    "ı": "i", "Ş": "S", "ş": "s",
    "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u",
    "Ö": "O", "ö": "o", "Ç": "C", "ç": "c",
})

def re_sub(pat: str, repl: str, s: str) -> str:
    import re
    return re.sub(pat, repl, s)

def normalize_key(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    s = s.translate(_TR_MAP)
    s = s.lower()
    s = re_sub(r"[^\w]+", "_", s)
    s = re_sub(r"_{2,}", "_", s).strip("_")
    return s

def _first_existing(*paths: Union[str, Path]) -> Optional[Path]:
    for p in paths:
        if not p:
            continue
        p = Path(p)
        if p.exists():
            return p
    return None

def _guess_excel_dir_from_cfg(cfg: Any) -> Optional[Path]:
    if cfg is None:
        return None
    try:
        cand = _first_existing(
            getattr(getattr(cfg, "data", None), "excel_dir", None),
            getattr(getattr(cfg, "data", None), "path",       None),
            getattr(cfg, "data_path", None),
        )
        if cand:
            return Path(cand)
    except Exception:
        pass
    try:
        d = cfg.get("data", {}) if isinstance(cfg, dict) else {}
        cand = _first_existing(d.get("excel_dir"), d.get("path"), cfg.get("data_path"))
        if cand:
            return Path(cand)
    except Exception:
        pass
    return None

COL_ALIASES: Dict[str, str] = {
    "date": "date", "tarih": "date", "tarihi": "date",
    "open": "open", "acilis": "open", "açilis": "open", "açilis_fiyati": "open", "açilis_fiyati_": "open",
    "high": "high", "yuksek": "high", "yüksek": "high",
    "low" : "low" , "dusuk" : "low" , "düşük" : "low" ,
    "close":"close","kapanis":"close","kapanış":"close","son":"close","son_fiyat":"close","adj_close":"close",
    "volume":"volume","hacim":"volume","islem_hacmi":"volume","işlem_hacmi":"volume",
    "adet":"volume", "lot":"volume",
    "kapanis_fiyati":"close","kapanis_fiyat":"close",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for c in df.columns:
        key = normalize_key(c).strip("_")
        std = COL_ALIASES.get(key, key)
        rename_map[c] = std
    return df.rename(columns=rename_map)

def read_excels_long(cfg_or_path: Union[str, Path, Any],
                     dayfirst: bool = True,
                     engine: str = "openpyxl",
                     verbose: bool = False) -> pd.DataFrame:
    if isinstance(cfg_or_path, (str, Path)):
        excel_dir = Path(cfg_or_path)
    else:
        excel_dir = _guess_excel_dir_from_cfg(cfg_or_path)
    if not excel_dir or not Path(excel_dir).exists():
        raise FileNotFoundError(f"Excel klasörü bulunamadı: {excel_dir}")

    records: List[pd.DataFrame] = []
    excel_files = sorted(str(p) for p in Path(excel_dir).glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError(f"'{excel_dir}' altında .xlsx bulunamadı.")

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

                df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=dayfirst)
                df = df.dropna(subset=["date"])

                keep = [c for c in ["open","high","low","close","volume"] if c in df.columns]
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
        raise RuntimeError("Hiçbir sheet/çalışma sayfasından veri toplanamadı.")

    full = pd.concat(records, ignore_index=True)
    full = full.sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    if "close" in full.columns:
        full = full.dropna(subset=["close"])
    return full

__all__ = ["read_excels_long", "normalize_key", "normalize_columns"]
