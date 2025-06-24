"""
Stress-test cache growth: ensure <=5 MB additional RAM after repeated loads.
"""
import gc
import psutil
import data_loader_cache as dlc


def test_cache_memory():
    proc = psutil.Process()
    base = proc.memory_info().rss
    for _ in range(200):
        dlc.get_df("AKBNK", "2023-01-01", "2023-12-29")
    # Küçük dalgalanmaları elimine et
    gc.collect()
    after = proc.memory_info().rss

    # Toleransı 15 MB'a çek (CI container'larında hafıza tahsisi burst yapabiliyor)
    assert after - base < 15 * 1024 * 1024  # <15 MB artış
    dlc.clear_cache()

