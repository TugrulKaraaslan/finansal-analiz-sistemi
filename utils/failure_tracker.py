"""Track failed operations for later reporting.

Collected failures are stored globally so they can be summarized once
execution completes.
"""

from collections import defaultdict
from dataclasses import asdict, dataclass


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


def get_failures(as_dict: bool = False):
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
