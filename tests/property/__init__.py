"""Common test setup for property-based tests.

Ensures the optional :mod:`hypothesis` dependency is available; otherwise
the entire ``tests.property`` package is skipped. This mirrors the
behaviour of :func:`pytest.importorskip` and avoids ``ImportError`` during
test collection when the dependency is missing.
"""

import pytest

pytest.importorskip("hypothesis")
