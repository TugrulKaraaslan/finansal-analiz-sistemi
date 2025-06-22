import runpy

if __name__ == "__main__":
    runpy.run_module("run", run_name="__main__")
else:
    from run import (
        veri_yukle,
        on_isle,
        indikator_hesapla,
        filtre_uygula,
        backtest_yap,
        raporla,
        calistir_tum_sistemi,
        run_pipeline,
    )  # noqa: F401
