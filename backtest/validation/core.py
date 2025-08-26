import ast

import pandas as pd

from backtest.dsl import DSLError, parse_expression
from backtest.naming import (
    CANONICAL_SET,
    normalize_indicator_token,
)

from .errors import ValidationError
from .report import ValidationReport


def validate_filters(
    filters_df: pd.DataFrame,
    alias_map: dict[str, str] | None = None,
) -> ValidationReport:
    df = filters_df
    report = ValidationReport()

    if list(df.columns) != ["FilterCode", "PythonQuery"]:
        raise ValidationError("filters.csv hatalı başlık", code="VC999")

    seen_codes = set()
    alias_map = alias_map or {}

    for i, row in df.iterrows():
        code = str(row.get("FilterCode", "")).strip()
        expr = str(row.get("PythonQuery", "")).strip()

        # FilterCode boş/tekrarlı
        if not code:
            report.add_error(i + 2, "VC001", "FilterCode boş")
        if code in seen_codes:
            report.add_error(i + 2, "VC001", f"FilterCode tekrarı: {code}")
        seen_codes.add(code)

        # PythonQuery boş
        if not expr or expr.lower() == "nan":
            report.add_error(i + 2, "VC002", "PythonQuery boş")
            continue

        # DSL parse kontrolü
        try:
            tree = parse_expression(expr)
        except DSLError as e:
            report.add_error(i + 2, e.code or "DF001", f"DSL hatası: {e}")
            continue

        # AST içindeki isimleri çıkar
        names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]
        for name in names:
            norm = normalize_indicator_token(name, alias_map)
            if norm not in CANONICAL_SET:
                report.add_error(
                    i + 2,
                    "VF001",
                    f"Bilinmeyen seri adı: {name}",
                )

    return report


__all__ = ["validate_filters", "ValidationError", "ValidationReport"]
