def unique_name(base: str, seen: set[str]) -> str:
    """Return a unique column name by appending _1, _2, ..."""
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
