"""Re-export helpers from the root ``report_generator`` module."""

from importlib import import_module

_rg = import_module("report_generator")

# Expose every public symbol defined by the top-level module so that
# ``finansal_analiz_sistemi.report_generator`` mirrors its API.
for _name in getattr(_rg, "__all__", []):
    globals()[_name] = getattr(_rg, _name)

__all__ = list(getattr(_rg, "__all__", []))
