"""Generate collision-free column names.

The :func:`unique_name` helper appends a numeric suffix to ``base`` when the
name already exists in ``seen`` so subsequent calls never clash with prior
results.
"""

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str]) -> str:
    """Return a unique column name derived from ``base``.

    The chosen label is added to ``seen`` so subsequent calls with the same
    base avoid duplicates. When ``base`` already exists, the lowest unused
    integer suffix is appended.

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

    # Collect existing numeric suffixes to avoid linear probing on
    # large ``seen`` sets. Non-numeric endings are ignored so custom
    # names like ``foo_bar`` do not interfere with the counter.
    suffixes = {
        int(name.rsplit("_", 1)[1])
        for name in seen
        if name.startswith(f"{base}_") and name.rsplit("_", 1)[-1].isdigit()
    }
    index = 1
    while index in suffixes:
        index += 1
    new = f"{base}_{index}"
    seen.add(new)
    return new
