import pytest

from backtest.config import load_config


CFG_BASE = """
project:
  out_dir: out
data:
  excel_dir: data
  filters_csv: filters.csv
benchmark:
  {key}: {value}
"""


@pytest.mark.parametrize(
    "key,value,expected_attr",
    [
        ("xu100_source", "csv", "source"),
        ("xu100_csv_path", "bist.csv", "csv_path"),
    ],
)
def test_legacy_key_individual(tmp_path, key, value, expected_attr):
    cfg_text = CFG_BASE.format(key=key, value=value)
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(cfg_text, encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "filters.csv").write_text(
        "FilterCode;PythonQuery\nF1;close>0\n", encoding="utf-8"
    )
    if key == "xu100_csv_path":
        (tmp_path / "bist.csv").write_text(
            "date,close\n2024-01-01,1\n", encoding="utf-8"
        )
    with pytest.warns(DeprecationWarning) as record:
        cfg = load_config(cfg_file)
    assert getattr(cfg.benchmark, expected_attr) == (
        str(tmp_path / value) if key == "xu100_csv_path" else value
    )
    assert len(record) == 1
    assert (
        str(record[0].message)
        == f"Legacy key 'benchmark.{key}' is deprecated; use 'benchmark.{expected_attr}' instead."
    )


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
    (tmp_path / "filters.csv").write_text(
        "FilterCode;PythonQuery\nF1;close>0\n", encoding="utf-8"
    )
    (tmp_path / "bist.csv").write_text(
        "date,close\n2024-01-01,1\n", encoding="utf-8"
    )
    with pytest.warns(DeprecationWarning) as record:
        cfg = load_config(cfg_file)
    assert cfg.benchmark.source == "csv"
    assert cfg.benchmark.csv_path.endswith("bist.csv")
    messages = {str(w.message) for w in record}
    assert (
        "Legacy key 'benchmark.xu100_source' is deprecated; use 'benchmark.source' instead."
        in messages
    )
    assert (
        "Legacy key 'benchmark.xu100_csv_path' is deprecated; use 'benchmark.csv_path' instead."
        in messages
    )
    assert len(record) == 2
