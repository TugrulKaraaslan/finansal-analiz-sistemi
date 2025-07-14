"""Test fixtures and configuration.

This module provides environment patches and helpers used across the
test suite.  It sanitizes ``sys.modules`` for Hypothesis and prevents
accidental HTTP requests during runs.
"""

import logging
import sys
from types import ModuleType, SimpleNamespace

try:
    import hypothesis
except Exception:  # pragma: no cover - optional dependency missing
    hypothesis = None
import numpy as np  # required for existing test helpers
import pandas as pd  # required for existing test helpers
import pytest  # required for pytest fixtures
import responses

# Ensure runtime patches (e.g., numpy.NaN) are applied early
import sitecustomize

_ = sitecustomize  # ensure side-effects


def _sanitize_sys_modules() -> None:
    """Ensure all ``sys.modules`` entries are hashable for Hypothesis.

    Detect items that are not real :class:`ModuleType` instances, create a
    new ``ModuleType`` with the same name and copy their attributes so that
    ``sys.modules`` only contains hashable objects.
    """
    fixed: dict[str, ModuleType] = {}
    for name, mod in list(sys.modules.items()):
        if isinstance(mod, ModuleType):
            continue
        safe_mod = ModuleType(name)
        attrs = getattr(mod, "__dict__", None)
        if isinstance(attrs, dict):
            safe_mod.__dict__.update(attrs)
        else:  # pragma: no cover - rare edge case
            try:
                safe_mod.__dict__.update(vars(mod))
            except Exception:
                pass
        fixed[name] = safe_mod
    if fixed:
        logging.getLogger(__name__).debug(
            "sys.modules temizlik: %d girdi düzeltildi", len(fixed)
        )
        sys.modules.update(fixed)


# Hypothesis scans ``sys.modules`` during test collection. Apply the patch
# immediately to avoid collection-time errors.
_sanitize_sys_modules()

if hypothesis is not None:
    hypothesis.settings.register_profile(
        "ci",
        max_examples=10,
        deadline=1000,
    )
    hypothesis.settings.load_profile("ci")

# Provide a minimal ``__hash__`` for ``SimpleNamespace`` so Hypothesis can
# create sets without failing.
if not hasattr(SimpleNamespace, "__hash__"):
    SimpleNamespace.__hash__ = lambda self: id(self)


@pytest.fixture(autouse=True)
def _fix_sys_modules():
    """Ensure newly imported modules are hashable for Hypothesis."""
    _sanitize_sys_modules()
    yield


@pytest.fixture(autouse=True)
def _mock_http():
    """Isolate tests from external HTTP calls."""
    with responses.RequestsMock() as rsps:
        rsps.add_passthru("http://localhost")
        yield


@pytest.fixture
def big_df() -> pd.DataFrame:
    """Return a large DataFrame for performance-oriented tests."""
    rows = 10_000
    return pd.DataFrame(
        {
            "hisse_kodu": ["AAA"] * rows,
            "tarih": pd.date_range("2024-01-01", periods=rows, freq="min"),
            "open": np.random.rand(rows),
            "high": np.random.rand(rows),
            "low": np.random.rand(rows),
            "close": np.random.rand(rows),
            "volume": np.random.randint(1, 1000, rows),
        }
    )


def pytest_sessionstart(session: pytest.Session) -> None:
    """Clean up ``sys.modules`` before the test session starts."""
    _sanitize_sys_modules()
