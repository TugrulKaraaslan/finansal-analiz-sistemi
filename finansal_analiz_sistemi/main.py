from __future__ import annotations

import importlib.util
import runpy
from pathlib import Path

_RUN_PATH = Path(__file__).resolve().parents[1] / "run.py"


def _load_run_module():
    spec = importlib.util.spec_from_file_location("run", _RUN_PATH)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise ImportError(f"Cannot load run module from {_RUN_PATH}")


if __name__ == "__main__":  # pragma: no cover - manual execution path
    runpy.run_path(_RUN_PATH, run_name="__main__")
else:
    _run = _load_run_module()

    backtest_yap = _run.backtest_yap  # noqa: F401
    calistir_tum_sistemi = _run.calistir_tum_sistemi  # noqa: F401
    filtre_uygula = _run.filtre_uygula  # noqa: F401
    indikator_hesapla = _run.indikator_hesapla  # noqa: F401
    on_isle = _run.on_isle  # noqa: F401
    raporla = _run.raporla  # noqa: F401
    run_pipeline = _run.run_pipeline  # noqa: F401
    veri_yukle = _run.veri_yukle  # noqa: F401
