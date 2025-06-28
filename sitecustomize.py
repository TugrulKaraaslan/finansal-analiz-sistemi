import types

# Ensure SimpleNamespace is hashable for Hypothesis set-operations
if getattr(types.SimpleNamespace, "__hash__", None) is None:
    def _simple_namespace_hash(self) -> int:
        """Hash SimpleNamespace by identity, satisfies flake8 E731."""
        return id(self)

    # Bind the function once so Hypothesis can safely hash the stubs
    types.SimpleNamespace.__hash__ = _simple_namespace_hash
