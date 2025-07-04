"""Compatibility wrapper for top-level report_generator module."""

from importlib import import_module

_rg = import_module("report_generator")

save_hatalar_excel = _rg.save_hatalar_excel

__all__ = ["save_hatalar_excel"]
