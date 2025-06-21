from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class FailedFilter:
    item: str
    reason: str
    hint: str = ""


failures = defaultdict(list)  # {'indicators': [...], 'filters': [...], ...}


def log_failure(category: str, item: str, reason: str, hint: str = "") -> None:
    """Log a failure under given category."""
    failures[category].append(FailedFilter(item, reason, hint))


def get_failures(as_dict: bool = False):
    if as_dict:
        return {c: [asdict(r) for r in rows] for c, rows in failures.items()}
    return failures
