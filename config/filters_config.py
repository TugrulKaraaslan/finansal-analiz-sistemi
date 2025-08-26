from __future__ import annotations

from typing import Any

from filters.module_loader import DEFAULT_FILTERS_MODULE, load_filters_from_module


def _load_filter_codes(cfg: dict[str, Any] | None = None) -> list[str]:
    """Return list of filter codes from a filters module.

    Parameters
    ----------
    cfg:
        Optional configuration mapping. ``filters.module`` defines the import
        path of the module providing filter definitions. ``filters.include`` can
        specify ``fnmatch`` patterns for selecting a subset of filters.
    """

    cfg = cfg or {}
    filters_cfg = cfg.get("filters", {})
    module_path = filters_cfg.get("module", DEFAULT_FILTERS_MODULE)
    include = filters_cfg.get("include", ["*"])
    df = load_filters_from_module(module_path, include)
    return df["FilterCode"].dropna().astype(str).tolist()


FILTER_LIST: list[str] = _load_filter_codes()
if not isinstance(FILTER_LIST, list):  # pragma: no cover - defensive
    raise TypeError("FILTER_LIST must be a list of strings")

__all__ = ["FILTER_LIST", "_load_filter_codes"]
