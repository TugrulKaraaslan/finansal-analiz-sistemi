"""Generate collision-free column names.

The :func:`unique_name` helper appends a numeric suffix to ``base`` when the
name already exists in ``seen`` so subsequent calls never clash with prior
results.
"""

import re

__all__ = ["unique_name"]


def unique_name(base: str, seen: set[str], *, delimiter: str = "_") -> str:
    """Return a unique column name derived from ``base``.

    The chosen label is added to ``seen`` so subsequent calls with the same
    base avoid duplicates. When ``base`` already exists, the lowest unused
    integer suffix is appended. Trailing delimiters are handled so callers
    can supply names like ``"foo_"`` without producing ``"foo__1"``.

    Parameters
    ----------
    base : str
        Desired column name.
    seen : set[str]
        Set of names already in use; updated in-place.
    delimiter : str, optional
        Character used between ``base`` and the numeric suffix.

    Returns
    -------
    str
        ``base`` itself if unused, otherwise a numbered variant such as
        ``base_1``.

    Raises
    ------
    ValueError
        If ``base`` is an empty string.
    """

    if not base:
        raise ValueError("base must be a non-empty string")

    if base not in seen:
        seen.add(base)
        return base

    prefix = base.rstrip(delimiter)
    pattern = rf"^{re.escape(prefix)}{re.escape(delimiter)}(\d+)$"
    suffixes = {int(m.group(1)) for name in seen if (m := re.match(pattern, name))}
    index = 1
    while index in suffixes:
        index += 1
    new = f"{prefix}{delimiter}{index}"
    seen.add(new)
    return new
