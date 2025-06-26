"""Global yapi landirma sabitleri."""

from pathlib import Path

import yaml

CACHE_PATH: Path = Path("veri/birlesik_hisse_verileri.parquet")
DEFAULT_CSV_PATH: Path = Path("data/raw/all_prices.csv")

# dtype downcast mappings for CSV reading
DTYPES = {
    "open": "float32",
    "high": "float32",
    "low": "float32",
    "close": "float32",
    "volume": "int32",
}

# final dataframe dtypes
DTYPES_MAP = {
    "open": "float32",
    "high": "float32",
    "low": "float32",
    "close": "float32",
    "volume": "int32",
    # common indicators
    "macd": "float32",
    "ema_10": "float32",
    "ema_20": "float32",
    "sma_20": "float32",
    "adx_14": "float32",
}

# chunk size for indicator calculation
CHUNK_SIZE: int = 1

# minimal indicator subset used by memory test
CORE_INDICATORS = [
    "ema_10",
    "ema_20",
    "rsi_14",
    "macd",
]

# load optional YAML config for runtime options
_cfg_path = os.path.join(os.path.dirname(__file__), "config.yml")
if os.path.exists(_cfg_path):
    with open(_cfg_path) as f:
        cfg = yaml.safe_load(f) or {}
else:
    cfg = {}
