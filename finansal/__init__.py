"""Public shortcuts for the :mod:`finansal` package.

This module exposes commonly used helpers so callers can simply import
them from ``finansal`` without referring to the submodules directly.
"""

from importlib import import_module

ParquetCacheManager = import_module("finansal.parquet_cache").ParquetCacheManager
lazy_chunk = import_module("finansal.utils").lazy_chunk
safe_set = import_module("finansal.utils").safe_set

__all__ = ["ParquetCacheManager", "lazy_chunk", "safe_set"]
