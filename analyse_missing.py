import argparse
import sys
import re
from pathlib import Path
from difflib import get_close_matches

import pandas as pd


def standardize_name(name: str) -> str:
    """Insert underscore between letters and numbers if missing."""
    return re.sub(r"(?<=\D)(?=\d)|(?<=\d)(?=\D)", "_", name)


def extract_columns(text: str) -> list[str]:
    if not text or text == "-" or pd.isna(text):
        return []
    candidates = re.findall(r"[A-Za-z0-9_]+", str(text))
    return [c for c in candidates if not c.isdigit()]


def scan_project_columns(py_files: list[Path]) -> set[str]:
    names: set[str] = set()
    pattern = re.compile(r"[\'\"]([A-Za-z0-9_]+)[\'\"]")
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        names.update(pattern.findall(text))
    return names


def column_exists(col: str, py_files: list[Path]) -> bool:
    pattern = re.compile(rf"['\"]{re.escape(col)}['\"]")
    for f in py_files:
        try:
            if pattern.search(f.read_text(encoding="utf-8")):
                return True
        except Exception:
            continue
    return False


def column_calculated(col: str, py_files: list[Path]) -> bool:
    assign_pattern = re.compile(rf"\['{re.escape(col)}'\]|\[\"{re.escape(col)}\"\]")
    for f in py_files:
        try:
            if assign_pattern.search(f.read_text(encoding="utf-8")):
                return True
        except Exception:
            continue
    return False


def analyse(df: pd.DataFrame, project_root: Path) -> pd.DataFrame:
    py_files = list(project_root.glob("**/*.py"))
    all_names = scan_project_columns(py_files)
    results = []
    for _, row in df.iterrows():
        missing_cols = extract_columns(row.get("eksik_ad"))
        if not missing_cols:
            missing_cols = extract_columns(row.get("detay"))
        for col in missing_cols:
            orig_col = col
            std_col = standardize_name(col)
            cause = ""
            suggestion = ""
            if column_exists(std_col, py_files):
                if column_calculated(std_col, py_files):
                    continue
                else:
                    cause = "hesaplanmamış gösterge"
                    suggestion = f"{std_col} hesaplamasını ekleyin"
            else:
                close = get_close_matches(std_col, all_names, n=1, cutoff=0.8)
                if close:
                    cause = "isim uyuşmazlığı"
                    suggestion = f"{std_col} yerine {close[0]} kullanılıyor"
                else:
                    if re.search(r"_keser_.*_(yukari|asagi)", std_col):
                        cause = "türetilmedi"
                    else:
                        cause = "hesaplanmamış gösterge"
                    suggestion = f"{std_col} hesaplamasını ekleyin"
            results.append(
                {
                    "filtre_kod": row.get("filtre_kod"),
                    "eksik_sutun": orig_col,
                    "muhtemel_sebep": cause,
                    "cozum_onerisi": suggestion,
                    "orijinal_detay": row.get("detay"),
                }
            )
    return pd.DataFrame(results)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True)
    parser.add_argument("--project_root", required=True)
    args = parser.parse_args()

    df = pd.read_excel(args.excel, sheet_name="Hatalar", engine="openpyxl")
    df = df[df["hata_tipi"] == "QUERY_ERROR"].copy()

    summary = analyse(df, Path(args.project_root))
    if not summary.empty:
        summary.to_csv("eksik_ozet.csv", index=False)
        summary.to_markdown("eksik_ozet.md", index=False)

    top_filt = df["filtre_kod"].nunique()
    uniq_cols = summary["eksik_sutun"].nunique() if not summary.empty else 0
    print(f"Toplam {top_filt} filtrede {uniq_cols} benzersiz eksik sütun bulundu.")

    return 1 if uniq_cols > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
