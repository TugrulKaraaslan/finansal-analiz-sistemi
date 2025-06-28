"""Entry point for running the project as a module or script."""

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    runpy.run_module("run", run_name="__main__")
else:
    from run import (  # noqa: F401
        backtest_yap,
        calistir_tum_sistemi,
        filtre_uygula,
        indikator_hesapla,
        on_isle,
        raporla,
        run_pipeline,
        veri_yukle,
    )
