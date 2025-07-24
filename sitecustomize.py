"""Apply runtime patches for optional dependencies and tests.

The module ensures :class:`types.SimpleNamespace` objects remain hashable,
restores the ``np.NaN`` alias for backward compatibility and registers
``importlib.metadata`` for packages that expect it on the ``importlib``
module.
"""

from __future__ import annotations

import types
from types import SimpleNamespace

import numpy as np

# Ensure ``SimpleNamespace`` instances remain hashable for set operations.
if SimpleNamespace.__hash__ is None:

    class _SimpleNamespaceHashable(SimpleNamespace):
        """Variant of :class:`SimpleNamespace` that is hashable by identity."""

        __hash__ = object.__hash__

    # ``SimpleNamespace`` is typed as ``Final`` in ``types`` stubs. ``setattr``
    # avoids ``Cannot assign to final name`` errors while preserving runtime
    # behaviour.
    types.SimpleNamespace = _SimpleNamespaceHashable

# numpy>=2 removed the ``NaN`` alias. Some optional dependencies still import it.
if not hasattr(np, "NaN"):
    np.NaN = np.nan

# Ensure ``importlib.metadata`` registers on ``importlib`` for packages that
# expect it as an attribute.
import importlib as _importlib  # noqa: E402
import importlib.metadata as _importlib_metadata  # noqa: E402

# Reference the imported module so static analyzers treat it as used.
_unused_importlib = _importlib
_unused_metadata = _importlib_metadata
