import config_loader


def test_clear_cache_refreshes_results(tmp_path):
    csv = tmp_path / "filters.csv"
    csv.write_text("PythonQuery\nclose_keser_open_yukari")
    first = config_loader.load_crossover_names(csv)
    csv.write_text("PythonQuery\nclose_keser_open_asagi")
    cached = config_loader.load_crossover_names(csv)
    assert cached == first
    config_loader.clear_cache()
    refreshed = config_loader.load_crossover_names(csv)
    assert refreshed != first
