import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from finansal_analiz_sistemi import config

# Regex to capture any crossover column name
CROSSOVER_NAME_RE = re.compile(r"([A-Za-z0-9_]+_keser_[A-Za-z0-9_]+_(?:yukari|asagi))")
EMA_CLOSE_RE = re.compile(r"ema_(\d+)_keser_close_(yukari|asagi)")


@lru_cache(maxsize=1)
def load_crossover_names(csv_path: str | Path | None = None) -> list[str]:
    """Parse filter CSV and config to collect crossover column names."""
    path = Path(csv_path or config.FILTRE_DOSYA_YOLU)
    names: set[str] = set()
    try:
        df = pd.read_csv(path, sep=";", engine="python")
    except Exception:
        df = pd.DataFrame()
    if "PythonQuery" in df.columns:
        for expr in df["PythonQuery"].dropna().astype(str):
            names.update(CROSSOVER_NAME_RE.findall(expr))
    for _, _, above, below in getattr(config, "SERIES_SERIES_CROSSOVERS", []):
        names.update([above, below])
    for col, _, suff in getattr(config, "SERIES_VALUE_CROSSOVERS", []):
        suf = str(suff).replace(".", "p")
        names.update([f"{col}_keser_{suf}_yukari", f"{col}_keser_{suf}_asagi"])
    return sorted(names)


def load_ema_close_crossovers(csv_path: str | Path | None = None) -> list[str]:
    """Return crossover names of the form 'ema_N_keser_close_*'."""
    return [n for n in load_crossover_names(csv_path) if EMA_CLOSE_RE.fullmatch(n)]
