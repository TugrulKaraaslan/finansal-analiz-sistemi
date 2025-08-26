"""Example embedded filters used in Colab config.

The CLI loads these definitions via ``filters.module`` configuration.
"""
from __future__ import annotations

from typing import List, Dict

FILTERS: List[Dict[str, str]] = [
    {"FilterCode": "T1", "PythonQuery": "close > open"},
    {"FilterCode": "T2", "PythonQuery": "sma_5 > sma_10"},
]


def get_filters() -> List[Dict[str, str]]:
    """Return available filter definitions.

    The structure matches ``filters.csv`` rows with ``FilterCode`` and
    ``PythonQuery`` keys.
    """
    return FILTERS
