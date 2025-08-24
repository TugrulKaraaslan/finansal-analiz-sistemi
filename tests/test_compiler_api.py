from __future__ import annotations

import subprocess

import pandas as pd
import pytest

from backtest.filters_compile import compile_expression, compile_filters


def test_compile_expression_variants_normalize() -> None:
    s = pd.Series([0, 1, 2, 1, 2, 3])
    df = pd.DataFrame({"a": s, "b": s.shift(1).fillna(0)})

    exprs = [
        "CROSSUP(a,b)",
        "crossOver(a,b)",
        "keser_yukari(a,b)",
        "cross_up(a,b)",
    ]
    results = [compile_expression(e)(df) for e in exprs]
    first = results[0]
    for res in results[1:]:
        pd.testing.assert_series_equal(first, res)


def test_compile_expression_input_validation() -> None:
    for bad in ["", " \t", None]:
        with pytest.raises(ValueError):
            compile_expression(bad)  # type: ignore[arg-type]


def test_compile_filters_sequence_and_callable() -> None:
    df = pd.DataFrame({"a": [1, 2, 3], "b": [3, 2, 1]})
    exprs = ["a > b", "b > a"]
    funcs = compile_filters(exprs)
    assert len(funcs) == 2
    assert all(callable(f) for f in funcs)
    out = [f(df) for f in funcs]
    pd.testing.assert_series_equal(out[0], df["a"] > df["b"])
    pd.testing.assert_series_equal(out[1], df["b"] > df["a"])


def test_no_other_compile_defs() -> None:
    part1 = "def compile_" + "expression"
    part2 = "def compile_" + "filters"
    pattern = part1 + "\\|" + part2
    cmd = (
        f'grep -RIn "{pattern}" backtest tools tests | '
        'grep -v "backtest/filters_compile.py" | grep -v "tests/test_compiler_api.py" || true'
    )
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    assert proc.stdout.strip() == ""
