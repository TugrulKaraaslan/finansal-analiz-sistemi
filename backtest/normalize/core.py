from __future__ import annotations
from typing import Iterable, Dict, Tuple, Literal
import re
import pandas as pd

from backtest.naming import load_alias_map, normalize_indicator_token
from .errors import CollisionError, AliasHeaderError
from .report import NormalizeReport

BuildPolicy = Literal["strict", "prefer_first", "suffix"]
_DOT_COPY = re.compile(r"^(?P<base>.*)\.\d+$")  # Close.1, Volume.2


def _canonicalize(name: str, alias_map: dict | None) -> str:
    # 1) alias çözümü; 2) snake_case’e dönüş (naming.normalize_indicator_token zaten yapıyor)
    return normalize_indicator_token(name, alias_map)


def build_column_mapping(columns: Iterable[str], alias_csv: str | None = None, *, policy: BuildPolicy = "strict") -> Tuple[Dict[str, str], NormalizeReport]:
    """
    Girdi kolonları için alias→kanonik + snake_case mapping üret.
    Çakışma stratejisi `policy` ile belirlenir.
    Dönüş: (mapping, report)
    Hatalar: strict modda çakışma varsa CollisionError(VN001).
    """
    alias_map = None
    if alias_csv:
        try:
            alias_map = load_alias_map(alias_csv).mapping
        except ValueError as e:
            raise AliasHeaderError(str(e), code="VN003") from e

    mapping: Dict[str, str] = {}
    seen: Dict[str, list[str]] = {}  # canonical -> originals
    report = NormalizeReport()

    for col in columns:
        # Close.1 gibi kopyaları önce çıplak ada indir
        m = _DOT_COPY.match(col)
        base = m.group("base") if m else col
        canon = _canonicalize(base, alias_map)
        mapping[col] = canon
        seen.setdefault(canon, []).append(col)

    # Çakışma çözümü
    for canon, originals in list(seen.items()):
        if len(originals) <= 1:
            continue
        # çakışma var
        if policy == "strict":
            report.add_collision(canon, originals)
            raise CollisionError(f"Kanonik isim çakışması: {canon} <- {originals}", code="VN001")
        elif policy == "prefer_first":
            # ilkini tut, diğerlerini drop listesine ekle
            for dup in originals[1:]:
                report.dropped.append(dup)
                # mapping'te yine aynı kanonik kalır (dup'lar rename edilmiyor)
        elif policy == "suffix":
            # ilk orijinal kanonik adı alır; diğerlerine _dupN son eki eklenir
            for i, dup in enumerate(originals[1:], start=1):
                new_name = f"{canon}_dup{i}"
                mapping[dup] = new_name
                report.add_rename(dup, new_name)
        else:
            raise ValueError(f"Bilinmeyen policy: {policy}")

    report.mapping = mapping
    return mapping, report


def apply_mapping(df: pd.DataFrame, mapping: Dict[str, str], *, drop: Iterable[str] | None = None) -> pd.DataFrame:
    new_df = df.copy()
    if drop:
        new_df = new_df.drop(columns=list(drop), errors="ignore")
    return new_df.rename(columns=mapping)


def normalize_dataframe(df: pd.DataFrame, alias_csv: str | None = None, *, policy: BuildPolicy = "strict") -> Tuple[pd.DataFrame, NormalizeReport]:
    mapping, report = build_column_mapping(df.columns, alias_csv, policy=policy)
    # prefer_first ise drop listesi uygulanır; suffix ise rename listesi zaten mapping'te
    drop_cols = report.dropped if report.dropped else None
    out = apply_mapping(df, mapping, drop=drop_cols)
    return out, report
