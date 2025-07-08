"""Track failed operations and reasons for reporting."""

from collections import defaultdict
from dataclasses import asdict, dataclass


@dataclass
class FailedFilter:
    """Record a failed operation and the associated reason."""

    item: str
    reason: str
    hint: str = ""


# {'indicators': [...], 'filters': [...], ...}
failures: defaultdict[str, list[FailedFilter]] = defaultdict(list)


def clear_failures() -> None:
    """Reset global failures dict."""
    failures.clear()


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Record a failed item under ``category`` with an optional hint."""
    failures[category].append(FailedFilter(item, reason, hint))


def get_failures(as_dict: bool = False):
    """Return collected failures.

    When ``as_dict`` is ``True`` the result is returned as a plain dictionary
    suitable for serialization.
    """
    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures
