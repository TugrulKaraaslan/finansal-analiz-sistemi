"""Track failed operations for later reporting.

The helpers here collect failed indicators, filters, and other items so
they can be summarized after a run.
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
    """Return collected failures.

    Parameters
    ----------
    as_dict : bool, optional
        When ``True`` the failures are returned as a plain dictionary
        suitable for serialization.

    Returns
    -------
    dict[str, list[FailedFilter]] | defaultdict[str, list[FailedFilter]]
        Recorded failures.
    """
    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Record a failed item under ``category`` with an optional hint.

    Parameters
    ----------
    category : str
        Failure category such as ``"filters"`` or ``"indicators"``.
    item : str
        Name of the failed item.
    reason : str
        Localized failure reason.
    hint : str, optional
        Additional hint for resolving the failure.
    """
    failures[category].append(FailedFilter(item, reason, hint))
