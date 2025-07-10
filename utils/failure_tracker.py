"""Track failed operations for later reporting.

The helpers here collect failed indicators, filters and other items so
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
    """Reset global failures dict."""
    failures.clear()


def get_failures(as_dict: bool = False):
    """Return collected failures.

    When ``as_dict`` is ``True`` the result is returned as a plain dictionary
    suitable for serialization.
    """
    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Record a failed item under ``category`` with an optional hint."""
    failures[category].append(FailedFilter(item, reason, hint))
