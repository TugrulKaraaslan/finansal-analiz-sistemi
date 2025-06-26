"""Global yapi landirma sabitleri."""

from pathlib import Path

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

# chunk size for indicator calculation
CHUNK_SIZE: int = 1

# minimal indicator subset used by memory test
CORE_INDICATORS = [
    "ema_10",
    "ema_20",
    "rsi_14",
    "macd",
]
