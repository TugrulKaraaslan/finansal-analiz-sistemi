import warnings

from backtest.config import load_config


def test_legacy_keys(tmp_path):
    cfg_text = """
project:
  out_dir: out
data:
  excel_dir: data
  filters_csv: filters.csv
benchmark:
  xu100_source: csv
  xu100_csv_path: bist.csv
    """
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(cfg_text, encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "filters.csv").write_text("FilterCode;PythonQuery\nF1;close>0\n", encoding="utf-8")
    (tmp_path / "bist.csv").write_text("date,close\n2024-01-01,1\n", encoding="utf-8")
    with warnings.catch_warnings(record=True) as w:
        cfg = load_config(cfg_file)
    assert cfg.benchmark.source == "csv"
    assert cfg.benchmark.csv_path.endswith("bist.csv")
    assert any("deprecated" in str(wi.message).lower() for wi in w)
