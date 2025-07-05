from pathlib import Path

import pandas as pd
import pytest

from finansal_analiz_sistemi import data_loader

CSV_CONTENT = "col\n1\n2\n3"


@pytest.mark.parametrize("content,expected_rows", [(CSV_CONTENT, 3), ("col\n42", 1)])
def test_load_data_param(tmp_path: Path, content: str, expected_rows: int):
    p = tmp_path / "sample.csv"
    p.write_text(content)
    df = data_loader.load_data(str(p))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == expected_rows


def test_load_data_empty(tmp_path: Path):
    p = tmp_path / "empty.csv"
    p.write_text("")
    with pytest.raises(pd.errors.EmptyDataError):
        data_loader.load_data(str(p))


def test_load_data_cache_refresh(tmp_path: Path):
    p = tmp_path / "sample.csv"
    p.write_text("col\n1\n2")
    df1 = data_loader.load_data(str(p))
    assert len(df1) == 2
    p.write_text("col\n1")
    df2 = data_loader.load_data(str(p))
    assert len(df2) == 1


@pytest.mark.parametrize("colname", ["Date", "Tarih", "tarih", "TARİH", "Unnamed: 0"])
def test_standardize_date_column(colname):
    df = pd.DataFrame({colname: ["2025-03-07"]})
    out = data_loader._standardize_date_column(df, "dummy")
    assert "tarih" in out.columns
    assert out.columns.tolist().count("tarih") == 1


def test_standardize_date_column_no_match():
    df = pd.DataFrame({"x": [1]})
    out = data_loader._standardize_date_column(df, "dummy")
    assert out.columns.tolist() == ["x"]


def test_standardize_ohlcv_columns():
    df = pd.DataFrame(
        {
            "Açılış": [1],
            "Yüksek": [2],
            "Düşük": [0],
            "Kapanış": [1],
            "Miktar": [10],
        }
    )
    out = data_loader._standardize_ohlcv_columns(df, "dummy")
    assert set(["open", "high", "low", "close", "volume"]).issubset(out.columns)


def test_check_and_create_dirs(tmp_path: Path):
    new_dir = tmp_path / "nested"
    data_loader.check_and_create_dirs(new_dir)
    assert new_dir.exists()


def test_load_excel_katalogu_short(tmp_path: Path):
    df = pd.DataFrame({"a": range(10)})
    p = tmp_path / "s.xlsx"
    df.to_excel(p, index=False)
    assert data_loader.load_excel_katalogu(str(p)) is None


def test_load_excel_katalogu_long(tmp_path: Path):
    pytest.importorskip("pyarrow")
    df = pd.DataFrame({"a": range(252)})
    p = tmp_path / "s2.xlsx"
    df.to_excel(p, index=False)
    out = data_loader.load_excel_katalogu(str(p))
    assert out is not None
    assert len(out) == 252
    assert Path(str(p).replace(".xlsx", ".parquet")).exists()


def test_yukle_filtre_dosyasi_alias(tmp_path: Path):
    p = tmp_path / "f.csv"
    pd.DataFrame({"FilterCode": ["F1"]}).to_csv(p, sep=";", index=False)
    df = data_loader.yukle_filtre_dosyasi(p)
    assert list(df.columns) == ["filtre_kodu"]


def test_yukle_filtre_dosyasi_missing(tmp_path: Path):
    p = tmp_path / "f.csv"
    pd.DataFrame({"x": [1]}).to_csv(p, sep=";", index=False)
    with pytest.raises(KeyError):
        data_loader.yukle_filtre_dosyasi(p)
