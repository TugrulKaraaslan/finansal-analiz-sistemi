"""Helpers for generating unique DataFrame column names.

The :func:`unique_name` helper appends a numeric suffix to ``base`` when it
already exists in the provided set.
"""

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str]) -> str:
    """Return ``base`` or a numbered variant not present in ``seen``.

    The generated name is automatically added to ``seen`` so the function can
    be called repeatedly with the same set.

    Parameters
    ----------
    base : str
        Desired column name.
    seen : set[str]
        Set of names already in use.

    Returns
    -------
    str
        ``base`` itself if unused, otherwise ``base_1``, ``base_2`` and so on.
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
