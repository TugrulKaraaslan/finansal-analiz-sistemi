import runpy

if __name__ == "__main__":
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
