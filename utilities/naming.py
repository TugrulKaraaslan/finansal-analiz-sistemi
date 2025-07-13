"""Helpers for generating unique column names.

The :func:`unique_name` function appends an incrementing suffix to ``base`` when
the desired name already exists in ``seen`` and records the result so repeated
calls remain collision free.
"""

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str]) -> str:
    """Return a unique column name based on ``base``.

    The generated label is added to ``seen`` so repeated calls remain
    collision free.

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
