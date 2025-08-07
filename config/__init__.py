from __future__ import annotations

from .filters_config import FILTER_LIST
from .paths_config import DATA_PATH, OUTPUT_PATH, LOG_DIR
from .settings import START_DATE, CAPITAL
from .crossovers_config import (
    SERIES_SERIES_CROSSOVERS,
    SERIES_VALUE_CROSSOVERS,
)

__all__ = [
    "FILTER_LIST",
    "DATA_PATH",
    "OUTPUT_PATH",
    "LOG_DIR",
    "START_DATE",
    "CAPITAL",
    "SERIES_SERIES_CROSSOVERS",
    "SERIES_VALUE_CROSSOVERS",
]
