from __future__ import annotations

from pathlib import Path
import csv

# Path to the filters definition file relative to the repository root
_FILTERS_CSV = Path(__file__).resolve().parent.parent / "filters.csv"


def _load_filter_codes() -> list[str]:
    """Return list of filter codes from ``filters.csv`` if available.

    Raises
    ------
    ValueError
        If ``filters.csv`` lacks the required ``FilterCode`` column.
    """
    if not _FILTERS_CSV.exists():
        return []
    with _FILTERS_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        if "FilterCode" not in (reader.fieldnames or []):
            raise ValueError("filters.csv missing 'FilterCode' column")
        return [row["FilterCode"] for row in reader if row.get("FilterCode")]


FILTER_LIST: list[str] = _load_filter_codes()
if not isinstance(FILTER_LIST, list):  # pragma: no cover - defensive
    raise TypeError("FILTER_LIST must be a list of strings")

__all__ = ["FILTER_LIST"]
