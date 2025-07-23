"""Tests validating the parameterized data loader helpers."""

from pathlib import Path

import pandas as pd
import pytest

from finansal_analiz_sistemi import data_loader

CSV_CONTENT = "col\n1\n2\n3"


def test_check_and_create_dirs(tmp_path: Path):
    """Created directories should exist after invocation."""
    new_dir = tmp_path / "nested"
    created = data_loader.check_and_create_dirs(new_dir)
    assert new_dir.exists()
    assert created == [new_dir]


def test_load_data_cache_refresh(tmp_path: Path):
    """Reload data when the underlying CSV file changes."""
    p = tmp_path / "sample.csv"
    p.write_text("col\n1\n2")
    df1 = data_loader.load_data(str(p))
    assert len(df1) == 2
    p.write_text("col\n1")
    df2 = data_loader.load_data(str(p))
    assert len(df2) == 1


def test_load_data_empty(tmp_path: Path):
    """Attempting to load an empty file should raise ``EmptyDataError``."""
    p = tmp_path / "empty.csv"
    p.write_text("")
    with pytest.raises(pd.errors.EmptyDataError):
        data_loader.load_data(str(p))


@pytest.mark.parametrize("content,expected_rows", [(CSV_CONTENT, 3), ("col\n42", 1)])
def test_load_data_param(tmp_path: Path, content: str, expected_rows: int):
    """Loaded DataFrame should have the expected row count."""
    p = tmp_path / "sample.csv"
    p.write_text(content)
    df = data_loader.load_data(str(p))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == expected_rows


def test_load_excel_katalogu_long(tmp_path: Path):
    """Large Excel files should be loaded and saved as Parquet."""
    pytest.importorskip("pyarrow")
    df = pd.DataFrame({"a": range(252)})
    p = tmp_path / "s2.xlsx"
    df.to_excel(p, index=False)
    out = data_loader.load_excel_katalogu(str(p))
    assert out is not None
    assert len(out) == 252
    assert Path(str(p).replace(".xlsx", ".parquet")).exists()


def test_load_excel_katalogu_xls(tmp_path: Path):
    """``.xls`` files should also be cached as Parquet."""
    pytest.importorskip("pyarrow")
    df = pd.DataFrame({"a": range(252)})
    p = tmp_path / "s.xls"
    df.to_excel(p, index=False)
    out = data_loader.load_excel_katalogu(str(p))
    assert out is not None
    assert len(out) == 252
    assert p.with_suffix(".parquet").exists()


def test_load_excel_katalogu_short(tmp_path: Path):
    """Excel files under 252 rows should return ``None``."""
    df = pd.DataFrame({"a": range(10)})
    p = tmp_path / "s.xlsx"
    df.to_excel(p, index=False)
    assert data_loader.load_excel_katalogu(str(p)) is None


@pytest.mark.parametrize(
    "colname", ["Date", "Tarih", "tarih", "TARİH", "Unnamed: 0", "Unnamed: 1"]
)
def test_standardize_date_column(colname):
    """Rename various date column names to ``tarih`` consistently."""
    df = pd.DataFrame({colname: ["2025-03-07"]})
    out = data_loader._standardize_date_column(df, "dummy")
    assert "tarih" in out.columns
    assert out.columns.tolist().count("tarih") == 1


def test_standardize_date_column_unnamed_any_position():
    """Unnamed columns should be detected even when not first."""
    df = pd.DataFrame({"a": [1], "Unnamed: 3": ["2025-03-07"]})
    out = data_loader._standardize_date_column(df, "dummy")
    assert "tarih" in out.columns


def test_standardize_date_column_no_match():
    """Leave DataFrame unchanged when no date-like columns exist."""
    df = pd.DataFrame({"x": [1]})
    out = data_loader._standardize_date_column(df, "dummy")
    assert out.columns.tolist() == ["x"]


def test_yukle_filtre_dosyasi_alias(tmp_path: Path):
    """CSV files with ``FilterCode`` should be normalized."""
    p = tmp_path / "f.csv"
    pd.DataFrame({"FilterCode": ["F1"]}).to_csv(p, sep=";", index=False)
    df = data_loader.yukle_filtre_dosyasi(p)
    assert list(df.columns) == ["filtre_kodu"]


def test_yukle_filtre_dosyasi_missing(tmp_path: Path):
    """Loading a CSV without ``filtre_kodu`` should raise ``KeyError``."""
    p = tmp_path / "f.csv"
    pd.DataFrame({"x": [1]}).to_csv(p, sep=";", index=False)
    with pytest.raises(KeyError):
        data_loader.yukle_filtre_dosyasi(p)
