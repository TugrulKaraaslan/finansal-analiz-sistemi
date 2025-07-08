"""Helpers for generating unique column names."""

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str]) -> str:
    """Return ``base`` or a numbered variant not present in ``seen``.

    Parameters
    ----------
    base : str
        Desired column name.
    seen : set[str]
        Set of names already in use.

    Returns
    -------
    str
        ``base`` itself if unused, otherwise ``base_1``, ``base_2``, ...
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
