"""Pytest genel ayarları ve yardımcı araçlar."""

import logging
import sys
from types import ModuleType, SimpleNamespace

import numpy as np  # mevcut test yardımcıları için gerekli
import pandas as pd  # mevcut test yardımcıları için gerekli
import pytest  # pytest fixture’ları için gerekli
import hypothesis

# Ensure runtime patches (e.g., numpy.NaN) are applied early
import sitecustomize  # noqa: F401


def _sanitize_sys_modules() -> None:
    """Hypothesis'in ``unhashable module`` hatasını önle.

    ``sys.modules`` içinde gerçek :class:`ModuleType` olmayan girdileri tespit
    eder; aynı isimle yeni bir :class:`ModuleType` üretip orijinal
    öznitelikleri kopyalar. Böylece **hashable** hâle gelirler.
    """

    fixed: dict[str, ModuleType] = {}
    for name, mod in list(sys.modules.items()):
        if isinstance(mod, ModuleType):
            continue
        safe_mod = ModuleType(name)
        safe_mod.__dict__.update(getattr(mod, "__dict__", {}))
        fixed[name] = safe_mod
    if fixed:
        logging.getLogger(__name__).debug(
            "sys.modules temizlik: %d girdi düzeltildi", len(fixed)
        )
        sys.modules.update(fixed)


# Hypothesis, modüller toplanırken ``sys.modules``'u tarar.
# Hemen yama uygulayarak koleksiyon hatalarını önle.
_sanitize_sys_modules()

hypothesis.settings.register_profile(
    "ci",
    max_examples=10,
    deadline=1000,
)
hypothesis.settings.load_profile("ci")

# ``SimpleNamespace`` için basit bir ``__hash__`` ekleyerek Hypothesis'in
# set oluşturma sırasında hata vermemesini sağla.
if not hasattr(SimpleNamespace, "__hash__"):
    SimpleNamespace.__hash__ = lambda self: id(self)


@pytest.fixture
def big_df() -> pd.DataFrame:
    rows = 10_000
    return pd.DataFrame(
        {
            "hisse_kodu": ["AAA"] * rows,
            "tarih": pd.date_range("2024-01-01", periods=rows, freq="T"),
            "open": np.random.rand(rows),
            "high": np.random.rand(rows),
            "low": np.random.rand(rows),
            "close": np.random.rand(rows),
            "volume": np.random.randint(1, 1000, rows),
        }
    )


def pytest_sessionstart(session: pytest.Session) -> None:  # noqa: D401
    """Test oturumu başlamadan önce ``sys.modules``'u temizle."""

    _sanitize_sys_modules()
