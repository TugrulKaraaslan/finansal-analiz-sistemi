from __future__ import annotations

"""Filter definition validator for detecting cycles and invalid references."""

from typing import List

from filter_engine import (
    FILTER_DEFS,
    CyclicFilterError,
    MaxDepthError,
    evaluate_filter,
)


def validate_filters() -> List[str]:
    """Validate all filter definitions in ``FILTER_DEFS``.

    Returns a list of error messages. An empty list means validation succeeded.
    """

    errors: List[str] = []
    for fid in FILTER_DEFS:
        try:
            evaluate_filter(fid)
        except (CyclicFilterError, MaxDepthError, KeyError) as exc:
            errors.append(f"{fid}: {exc}")
    return errors
