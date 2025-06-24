"""
Stress-test cache growth: ensure <=5 MB additional RAM after repeated loads.
"""
import psutil
import data_loader_cache as dlc


def test_cache_memory():
    proc = psutil.Process()
    base = proc.memory_info().rss
    for _ in range(200):
        dlc.get_df("AKBNK", "2023-01-01", "2023-12-29")
    after = proc.memory_info().rss
    assert after - base < 5 * 1024 * 1024
    dlc.clear_cache()

