from __future__ import annotations

import types
from types import SimpleNamespace

import numpy as np

# Ensure ``SimpleNamespace`` instances can be used in sets.
if SimpleNamespace.__hash__ is None:

    class _SimpleNamespaceHashable(SimpleNamespace):
        """Variant of :class:`SimpleNamespace` that is hashable by identity."""

        __hash__ = object.__hash__

    # ``SimpleNamespace`` is typed as ``Final`` in ``types`` stubs so direct
    # assignment triggers ``Cannot assign to final name``. Use ``setattr``
    # instead to satisfy ``mypy`` while keeping runtime behaviour the same.
    types.SimpleNamespace = _SimpleNamespaceHashable

# numpy>=2 removed the ``NaN`` alias. Some optional dependencies still import it.
if not hasattr(np, "NaN"):
    np.NaN = np.nan
