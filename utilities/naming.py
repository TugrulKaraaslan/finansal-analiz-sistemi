"""Generate unique column names for DataFrames.

``unique_name`` appends an incrementing suffix to ``base`` when the desired
name already exists in ``seen``. The newly created name is inserted into
``seen`` before being returned so subsequent calls remain unique.
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
