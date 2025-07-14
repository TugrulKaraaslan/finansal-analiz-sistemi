"""Utility for generating unique column names.

The :func:`unique_name` helper appends an incrementing suffix when ``base``
already exists in ``seen`` so later calls avoid collisions.
"""

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str]) -> str:
    """Return a unique column name derived from ``base``.

    The chosen label is added to ``seen`` so subsequent calls with the same
    base avoid duplicates.

    Args:
        base: Desired column name.
        seen: Set of names already in use; updated in-place.

    Returns:
        str: ``base`` itself if unused, otherwise a numbered variant such as
        ``base_1``.
    """
    if base not in seen:
        seen.add(base)
        return base
    idx = 1
    new = f"{base}_{idx}"
    while new in seen:
        idx += 1
        new = f"{base}_{idx}"
    seen.add(new)
    return new
