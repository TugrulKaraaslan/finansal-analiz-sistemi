"""Generate collision-free column names.

The :func:`unique_name` helper appends a numeric suffix to ``base`` when the
name already exists in ``seen`` so subsequent calls never clash with prior
results.
"""

from __future__ import annotations

from typing import MutableSet

__all__ = ["unique_name"]


def unique_name(
    base: str,
    seen: MutableSet[str],
    *,
    delimiter: str = "_",
    start: int = 1,
) -> str:
    """Return a unique column name derived from ``base``.

    The chosen label is added to ``seen`` so subsequent calls with the same
    base avoid duplicates. When ``base`` already exists, the lowest unused
    integer suffix is appended. Trailing delimiters are handled so callers
    can supply names like ``"foo_"`` without producing ``"foo__1"``.

    Parameters
    ----------
    base : str
        Desired column name.
    seen : MutableSet[str]
        Set of names already in use. The collection is updated in-place.
    delimiter : str, optional
        Character used between ``base`` and the numeric suffix.
    start : int, optional
        Initial numeric suffix when ``base`` already exists. ``1`` by default.

    Returns
    -------
    str
        ``base`` itself if unused, otherwise a numbered variant such as
        ``base_1``.

    Raises
    ------
    ValueError
        If ``base`` is an empty string, ``start`` is less than ``1`` or
        ``delimiter`` is empty.
    """

    if not base:
        raise ValueError("base must be a non-empty string")
    if start < 1:
        raise ValueError("start must be >= 1")
    if not delimiter:
        raise ValueError("delimiter must be a non-empty string")

    if base not in seen:
        seen.add(base)
        return base

    if base.endswith(delimiter):
        prefix = base[: -len(delimiter)]
    else:
        prefix = base
    idx = start
    while True:
        candidate = f"{prefix}{delimiter}{idx}"
        if candidate not in seen:
            seen.add(candidate)
            return candidate
        idx += 1
