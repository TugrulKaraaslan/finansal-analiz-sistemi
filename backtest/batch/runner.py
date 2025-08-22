from __future__ import annotations
import ast
from typing import Iterable, Dict, Set
import pandas as pd

from backtest.normalize import normalize_dataframe
from backtest.validation import validate_filters
from backtest.dsl import Evaluator, SeriesContext, FUNCTIONS
from backtest.precompute import Precomputer
from backtest.batch.scheduler import trading_days
from backtest.batch.io import OutputWriter

# Yardımcı: DSL içindeki Name'leri çıkar
class _NameVisitor(ast.NodeVisitor):
    def __init__(self):
        self.names: Set[str] = set()
    def visit_Name(self, node: ast.Name):
        self.names.add(node.id)


def _extract_series_names(expr: str) -> Set[str]:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return set()
    vis = _NameVisitor(); vis.visit(tree)
    return vis.names


def run_scan_day(df: pd.DataFrame, day: str, filters_df: pd.DataFrame, *, alias_csv: str | None = None) -> list[tuple[str, str]]:
    """Tek bir gün için sinyal üret.
    Dönüş: [(symbol, filter_code), ...]
    Beklenti: df index=DatetimeIndex, kolonlar kanonik isimlerden oluşur (sembol çoklu ise MultiIndex kolon: (symbol, field)).
    Stage1 basitlik: df, tek sembol için de çalışır; çoklu sembol için column MultiIndex beklenir: top level=symbol, second level=field
    """
    rows: list[tuple[str, str]] = []

    # Çoklu sembol mü tek sembol mü algıla
    multi_symbol = isinstance(df.columns, pd.MultiIndex) and df.columns.nlevels == 2
    symbols: Iterable[str]
    if multi_symbol:
        symbols = sorted({c[0] for c in df.columns.unique()})
        
    else:
        symbols = ["SYMBOL"]  # tek sembol placeholder

    # Günlük slice
    d = pd.to_datetime(day)
    if d not in df.index:
        return rows

    # Filtrelerde geçen indikatör isimlerini topla
    indicators_needed: Set[str] = set()
    for _, r in filters_df.iterrows():
        expr = str(r["PythonQuery"]) if "PythonQuery" in r else ""
        for name in _extract_series_names(expr):
            if name in FUNCTIONS:
                continue
            if name not in ("open", "high", "low", "close", "volume", "vwap_d"):
                indicators_needed.add(name)

    # Ön hesaplayıcıyı sembol bazında uygula
    pc = Precomputer()

    if multi_symbol:
        # her sembol için alanları al, göstergeleri ekle
        frames: dict[str, pd.DataFrame] = {}
        for sym in symbols:
            sub = df.xs(sym, axis=1, level=0).copy()
            sub, _ = normalize_dataframe(sub, alias_csv, policy="prefer_first")
            sub = pc.precompute(sub, indicators_needed)
            sub = sub.apply(pd.to_numeric, errors="coerce")
            frames[sym] = sub
        # değerlendirme: her filtre için maske ve sinyal
        for _, r in filters_df.iterrows():
            code = str(r["FilterCode"]).strip()
            expr = str(r["PythonQuery"]).strip()
            for sym in symbols:
                ctx = SeriesContext(frames[sym].iloc[:])
                ev = Evaluator(ctx)
                mask = ev.eval(expr)
                if bool(mask.loc[d]):
                    rows.append((sym, code))
    else:
        # tek sembol
        sub, _ = normalize_dataframe(df.copy(), alias_csv, policy="prefer_first")
        sub = pc.precompute(sub, indicators_needed)
        sub = sub.apply(pd.to_numeric, errors="coerce")
        for _, r in filters_df.iterrows():
            code = str(r["FilterCode"]).strip()
            expr = str(r["PythonQuery"]).strip()
            ctx = SeriesContext(sub.iloc[:])
            ev = Evaluator(ctx)
            mask = ev.eval(expr)
            if bool(mask.loc[d]):
                rows.append(("SYMBOL", code))

    return rows


def run_scan_range(df: pd.DataFrame, start: str, end: str, filters_df: pd.DataFrame, *, out_dir: str, alias_csv: str | None = None) -> None:
    # Dry-run: geçerlilik
    # Not: validate_filters CSV dosya yoluyla çalışır; burada DataFrame verildiği için kullanıcıdan paths alınır (CLI tarafında yapılır)
    writer = OutputWriter(out_dir)

    days = trading_days(df.index, start, end)
    if len(days) == 0:
        raise RuntimeError("BR002: tarih aralığı veriyle kesişmiyor")

    for day in days:
        rows = run_scan_day(df, str(day.date()), filters_df, alias_csv=alias_csv)
        writer.write_day(day, rows)
