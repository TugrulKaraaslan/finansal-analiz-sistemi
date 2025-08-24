import os
from pathlib import Path

# Project kökünü ve veri dizinini tek yerde tanımla. ENV ile override
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))

# Geri uyum için EXCEL_DIR env'i destekle; aksi halde DATA_DIR kullan
EXCEL_DIR = Path(os.getenv("EXCEL_DIR", DATA_DIR))

# Kanonik dosya yolları
BENCHMARK_PATH = EXCEL_DIR / "BIST.xlsx"
ALIAS_PATH = DATA_DIR / "alias_mapping.csv"


def project_root_from_config(config_path: str | Path) -> Path:
    config_path = Path(config_path).resolve()
    return (
        config_path.parent.parent
        if config_path.parent.name == "config"
        else config_path.parent
    )


def resolve_under_root(
    config_path: str | Path,
    maybe_path: str | Path,
) -> Path:
    p = Path(maybe_path)
    if p.is_absolute():
        return p
    root = project_root_from_config(config_path)
    return (root / p).resolve()


__all__ = [
    "project_root_from_config",
    "resolve_under_root",
    "PROJECT_ROOT",
    "DATA_DIR",
    "EXCEL_DIR",
    "BENCHMARK_PATH",
    "ALIAS_PATH",
]
