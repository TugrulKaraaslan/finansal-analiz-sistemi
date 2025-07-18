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

    import re

    pattern = re.compile(re.escape(base) + r"_(\d+)$")
    max_idx = 0
    for name in seen:
        match = pattern.fullmatch(name)
        if match:
            max_idx = max(max_idx, int(match.group(1)))

    new = f"{base}_{max_idx + 1}"
    seen.add(new)
    return new
