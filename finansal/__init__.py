"""Convenience imports for frequently used ``finansal`` helpers.

Modules are imported lazily to keep startup overhead minimal while
providing straightforward access to core utilities.
"""

from __future__ import annotations

from importlib import import_module

ParquetCacheManager = import_module("finansal.parquet_cache").ParquetCacheManager
lazy_chunk = import_module("finansal.utils").lazy_chunk
safe_set = import_module("finansal.utils").safe_set

__all__ = ["ParquetCacheManager", "lazy_chunk", "safe_set"]
