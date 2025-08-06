# DÜZENLENDİ – SYNTAX TEMİZLİĞİ
from __future__ import annotations

import ast
import importlib
import importlib.util
import pkgutil
from pathlib import Path

import backtest


def _module_info(module_name: str) -> tuple[bool, bool]:
    """Return tuple(has_docstring, has_future_annotations)."""
    spec = importlib.util.find_spec(module_name)
    assert spec and spec.origin, f"Cannot find module {module_name}"
    source = Path(spec.origin).read_text(encoding="utf-8")
    tree = ast.parse(source)
    body = tree.body
    has_docstring = bool(
        body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Str)
    )
    idx = 1 if has_docstring else 0
    has_future_annotations = (
        len(body) > idx
        and isinstance(body[idx], ast.ImportFrom)
        and body[idx].module == "__future__"
        and any(n.name == "annotations" for n in body[idx].names)
    )
    return has_docstring, has_future_annotations


def test_import_all_backtest_modules():
    modules = [("backtest", Path(backtest.__file__))]
    modules.extend(
        (
            f"{backtest.__name__}.{m.name}",
            Path(importlib.util.find_spec(f"{backtest.__name__}.{m.name}").origin),
        )
        for m in pkgutil.iter_modules(backtest.__path__)
        if m.name != "__main__"
    )

    seen_with_doc = False
    seen_without_doc = False

    for module_name, _ in modules:
        has_doc, has_future = _module_info(module_name)
        mod = importlib.import_module(module_name)
        assert mod is not None, f"Failed to import {module_name}"
        if has_future:
            if has_doc:
                seen_with_doc = True
            else:
                seen_without_doc = True

    assert (
        seen_with_doc
    ), "Expected a module with docstring and from __future__ import annotations"
    assert (
        seen_without_doc
    ), "Expected a module without docstring but with from __future__ import annotations"
