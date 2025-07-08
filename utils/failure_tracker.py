"""Track failed operations and reasons for reporting."""

from collections import defaultdict
from dataclasses import asdict, dataclass


@dataclass
class FailedFilter:
    item: str
    reason: str
    hint: str = ""


# {'indicators': [...], 'filters': [...], ...}
failures: defaultdict[str, list[FailedFilter]] = defaultdict(list)


def clear_failures() -> None:
    """Reset global failures dict."""
    failures.clear()


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Log a failure under given category."""
    failures[category].append(FailedFilter(item, reason, hint))


def get_failures(as_dict: bool = False):
    """Return collected failures."""

    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures
