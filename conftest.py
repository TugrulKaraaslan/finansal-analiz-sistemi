import types

import numpy as np
import pandas as pd
import pytest

"""Pytest genel ayarları – Hypothesis uyumluluk yamaları."""

import logging
import sys
from types import ModuleType, SimpleNamespace


def _sanitize_sys_modules() -> None:
    """`sys.modules` içindeki hash'lenemez girdileri kaldır/terfi et.

    Hypothesis >= 6.88, yerel sabitleri belirlerken `sys.modules.values()`
    kümesine ihtiyaç duyar.  `SimpleNamespace` hashable değildir ve
    `set()` dönüşümü sırasında `TypeError` fırlatır.  Bu yardımcı, test
    oturumunun başında hatalı girdileri güvenli hâle getirir.
    """
    patched = 0
    for name, mod in list(sys.modules.items()):
        if not isinstance(mod, ModuleType):
            safe_mod = ModuleType(name)
            # Varsa kullanıcı tanımlı attribute’ları taşı
            safe_mod.__dict__.update(getattr(mod, "__dict__", {}))
            sys.modules[name] = safe_mod
            patched += 1
    if patched:
        logging.getLogger(__name__).debug(
            "Hypothesis fix: %s hash'lenemez sys.modules girdisi ModuleType'a dönüştürüldü.",
            patched,
        )


_sanitize_sys_modules()

# Hypothesis scans sys.modules during test collection.  Our tests inject
# ``types.SimpleNamespace`` objects as stubs, but these are not hashable by
# default, which leads to ``TypeError`` when Hypothesis tries to create a set
# from module values.  Provide a simple ``__hash__`` implementation early so
# that test collection succeeds regardless of import order.
if not hasattr(types.SimpleNamespace, "__hash__"):
    types.SimpleNamespace.__hash__ = lambda self: id(self)


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


"""Pytest genel ayarları ve yardımcı araçlar."""
import logging  # noqa: E402
import sys  # noqa: E402
from types import ModuleType, SimpleNamespace  # noqa: E402,F401


def _sanitize_sys_modules() -> None:
    """Hypothesis'in `unhashable module` hatasını önle.

    `sys.modules` içinde gerçek `ModuleType` olmayan (örn. `SimpleNamespace`)
    girdileri tespit eder; aynı isimle yeni bir `ModuleType` üretip
    orijinal öznitelikleri kopyalar. Böylece **hashable** hâle gelirler.
    Çağrı maliyeti yok denecek kadar azdır ve production kodunu
    etkilemez – yalnızca test oturumunda çalışır.
    """

    fixed: dict[str, ModuleType] = {}
    for name, mod in list(sys.modules.items()):
        if isinstance(mod, ModuleType):
            continue  # zaten güvenli
        safe_mod = ModuleType(name)
        # SimpleNamespace ise dict kopyala; diğer durumlarda __dict__ yeterli
        attrs = getattr(mod, "__dict__", {})
        safe_mod.__dict__.update(attrs)
        fixed[name] = safe_mod
    if fixed:
        logging.getLogger(__name__).debug(
            "sys.modules temizlik: %d girdi düzeltildi", len(fixed)
        )
        sys.modules.update(fixed)


# pytest hook – test tüm dosyalar toplanmadan önce çalışır
def pytest_sessionstart(session):  # noqa: D401 – kısa açıklama yeterli
    _sanitize_sys_modules()
