from dataclasses import dataclass

__all__ = ["ValidationError"]


@dataclass
class ValidationError:
    hata_tipi: str
    eksik_ad: str
    detay: str
    cozum_onerisi: str
    reason: str
    hint: str
