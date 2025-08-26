"""Load filters from a Python module.

This utility provides a single entry point for obtaining filter definitions
from a Python module. The target module must expose either a ``FILTERS``
variable or a ``get_filters`` function that returns a list of dictionaries
with ``FilterCode`` and ``PythonQuery`` keys.
"""

from __future__ import annotations

from fnmatch import fnmatch
import importlib
from typing import Iterable

import pandas as pd

DEFAULT_FILTERS_MODULE = "io_filters"


def _extract_filters(mod) -> list[dict]:
    if hasattr(mod, "FILTERS"):
        return getattr(mod, "FILTERS")
    if hasattr(mod, "get_filters"):
        return mod.get_filters()
    raise ValueError("filters module missing FILTERS/get_filters")


def _filter_codes(df: pd.DataFrame, include: Iterable[str]) -> pd.DataFrame:
    patterns = list(include)
    mask = [any(fnmatch(code, p) for p in patterns) for code in df["FilterCode"]]
    return df[mask].reset_index(drop=True)


def load_filters_from_module(
    module_path: str | None,
    include: list[str] | None = None,
) -> pd.DataFrame:
    """Load filter definitions from a Python module.

    Parameters
    ----------
    module_path:
        Import path of the module containing filter definitions. If ``None``
        the :data:`DEFAULT_FILTERS_MODULE` value is used.
    include:
        Optional list of fnmatch patterns to select a subset of filters.
        Defaults to ``["*"]`` which selects all filters.
    """

    module_name = module_path or DEFAULT_FILTERS_MODULE
    mod = importlib.import_module(module_name)
    filters_list = _extract_filters(mod)
    df = pd.DataFrame(filters_list)

    required = ["FilterCode", "PythonQuery"]
    if any(col not in df.columns for col in required):
        raise ValueError(f"filters must contain columns {required!r}")

    patterns = include or ["*"]
    return _filter_codes(df, patterns)


__all__ = ["DEFAULT_FILTERS_MODULE", "load_filters_from_module"]
