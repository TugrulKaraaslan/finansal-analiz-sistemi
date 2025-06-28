import types

import numpy as np

# Ensure ``SimpleNamespace`` instances can be used in sets.
if types.SimpleNamespace.__hash__ is None:

    class _SimpleNamespaceHashable(types.SimpleNamespace):
        """Variant of :class:`SimpleNamespace` that is hashable by identity."""

        __hash__ = object.__hash__

    # Swap out the standard ``SimpleNamespace`` for the hashable variant.
    types.SimpleNamespace = _SimpleNamespaceHashable

# numpy>=2 removed the ``NaN`` alias. Some optional dependencies still import it.
if not hasattr(np, "NaN"):
    np.NaN = np.nan
