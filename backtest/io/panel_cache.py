from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtest.naming import normalize_dataframe_columns


def build_panel_parquet(
    src_excels: str | Path,
    out_path: str | Path,
    *,
    normalize: bool = True,
) -> str:
    """Read Excel files under ``src_excels`` into a single DataFrame and write to
    a parquet file located at ``out_path``.

    Parameters
    ----------
    src_excels : str or Path
        Directory containing source Excel files.
    out_path : str or Path
        Destination parquet file.
    normalize : bool, default True
        When set, column names are normalised to snake_case using
        :func:`backtest.naming.normalize_dataframe_columns`.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_dfs = []
    for f in Path(src_excels).glob("*.xlsx"):
        try:
            df = pd.read_excel(f)
            if normalize:
                mapping = normalize_dataframe_columns(df.columns)
                df = df.rename(columns=mapping)
            all_dfs.append(df)
        except Exception:
            continue
    if not all_dfs:
        raise FileNotFoundError("Panel oluşturulamadı; excel yok")
    panel = pd.concat(all_dfs, ignore_index=True)
    panel.to_parquet(out_path, index=False)
    return str(out_path)


def load_panel_parquet(out_path: str | Path) -> pd.DataFrame:
    """Load a previously cached panel parquet file."""
    return pd.read_parquet(out_path)
