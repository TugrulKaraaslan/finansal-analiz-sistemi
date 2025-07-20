from utils.memory_profile import MemoryProfile, mem_profile


def test_memory_profile_writes_row(tmp_path):
    path = tmp_path / "mp.csv"
    with MemoryProfile(path=path):
        [0] * 1000  # allocate memory
    assert path.exists()
    rows = path.read_text().strip().splitlines()
    assert len(rows) == 1
    ts, peak, diff = rows[0].split(",")
    assert float(ts) > 0
    assert float(peak) >= 0
    assert float(diff) >= 0


def test_mem_profile_alias():
    assert mem_profile is MemoryProfile


def test_memory_profile_accepts_string_path(tmp_path):
    """Path argument may be given as a string."""
    fname = tmp_path / "mp.csv"
    with MemoryProfile(path=str(fname)):
        pass
    assert fname.exists()
