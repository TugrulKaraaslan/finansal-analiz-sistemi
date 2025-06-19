from collections import defaultdict

failures = defaultdict(
    list
)  # {'indicators': [...], 'filters': [...], 'crossovers': []}


def log_failure(category: str, item: str, reason: str):
    """Log a failure under given category."""
    failures[category].append({"item": item, "reason": reason})


def get_failures():
    return failures
