"""Track failed operations for later reporting.

Failures are kept in a global dictionary so helpers can append entries
during execution and emit a summarized list after completion.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    import pandas as pd


@dataclass
class FailedFilter:
    """Record a failed operation and the associated reason."""

    item: str
    reason: str
    hint: str = ""


# Global record of failures per category, e.g. ``{"indicators": [], "filters": []}``
failures: defaultdict[str, list[FailedFilter]] = defaultdict(list)


def clear_failures() -> None:
    """Reset the global failures dictionary."""
    failures.clear()


def get_failures(
    as_dict: bool = False,
) -> Union[dict[str, list[FailedFilter]], defaultdict[str, list[FailedFilter]]]:
    """Return recorded failures.

    Args:
        as_dict (bool, optional): When ``True`` return a plain dictionary
            instead of the internal ``defaultdict`` structure.

    Returns:
        dict[str, list[FailedFilter]] | defaultdict[str, list[FailedFilter]]:
            Failures grouped by category.
    """
    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Record a failed item under ``category`` with an optional hint.

    Args:
        category (str): Failure category such as ``"filters"`` or ``"indicators"``.
        item (str): Name of the failed item.
        reason (str): Localized failure reason.
        hint (str, optional): Additional hint for resolving the failure.
    """
    failures[category].append(FailedFilter(item, reason, hint))


def failures_to_df() -> pd.DataFrame:
    """Return a ``DataFrame`` with all recorded failures.

    The resulting frame contains the columns ``category``, ``item``, ``reason``
    and ``hint``. The order of rows reflects the insertion order.
    """
    import pandas as pd

    records = [
        {
            "category": cat,
            "item": f.item,
            "reason": f.reason,
            "hint": f.hint,
        }
        for cat, rows in failures.items()
        for f in rows
    ]
    return pd.DataFrame.from_records(
        records, columns=["category", "item", "reason", "hint"]
    )
