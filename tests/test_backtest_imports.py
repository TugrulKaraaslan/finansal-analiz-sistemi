from __future__ import annotations

import importlib
import pkgutil

import backtest

def test_backtest_all_modules_importable():
    for module_info in pkgutil.iter_modules(backtest.__path__):
        name = module_info.name
        if name == "__init__":
            continue
        module_name = f"{backtest.__name__}.{name}"
        try:
            importlib.import_module(module_name)
        except (ImportError, SyntaxError) as exc:
            raise AssertionError(f"Failed to import {module_name}: {exc}")
