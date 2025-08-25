import warnings


def emit_deprecation(old_key: str, new_key: str, *, stacklevel: int = 2) -> None:
    """Emit standard deprecation warnings for legacy configuration keys."""
    warnings.warn(
        f"Legacy key '{old_key}' is deprecated; use '{new_key}' instead.",
        DeprecationWarning,
        stacklevel=stacklevel,
    )
