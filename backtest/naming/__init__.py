import warnings

import pandas as pd

from .alias_loader import AliasMap, load_alias_map
from .aliases import normalize_token
from .canonical import CANONICAL_BASE, CANONICAL_SET
from .legacy import *  # noqa: F401,F403
from .normalize import (
    normalize_dataframe_columns,
    normalize_indicator_token,
    to_snake,
)


def canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with canonicalised column names.

    All column names are normalised to lower ``snake_case`` using
    :func:`normalize_name` from the legacy naming helpers.  Duplicate columns
    are handled carefully:

    * If two columns normalise to the same name and contain identical data the
      duplicate is dropped.
    * If the data differs, the later column is suffixed with ``_2``, ``_3`` …
      and a :class:`UserWarning` is emitted.
    """

    rename_map = {col: normalize_name(col) for col in df.columns}
    out = df.rename(columns=rename_map).copy()

    seen: dict[str, pd.Series] = {}
    drops: list[int] = []
    new_names = list(out.columns)
    for i, col in enumerate(list(out.columns)):
        if col not in seen:
            seen[col] = out.iloc[:, i]
            continue
        first = seen[col]
        current = out.iloc[:, i]
        if first.equals(current):
            drops.append(i)
            continue
        suffix = 2
        new_name = f"{col}_{suffix}"
        while new_name in seen:
            suffix += 1
            new_name = f"{col}_{suffix}"
        warnings.warn(
            f"duplicate column '{col}' renamed to '{new_name}'",
            UserWarning,
            stacklevel=2,
        )
        new_names[i] = new_name
        seen[new_name] = current

    keep = [i for i in range(len(new_names)) if i not in drops]
    out = out.iloc[:, keep]
    out.columns = [new_names[i] for i in keep]
    return out


__all__ = [
    "CANONICAL_BASE",
    "CANONICAL_SET",
    "AliasMap",
    "load_alias_map",
    "to_snake",
    "normalize_indicator_token",
    "normalize_token",
    "normalize_dataframe_columns",
    "canonicalize_columns",
]
