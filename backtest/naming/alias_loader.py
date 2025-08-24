from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from backtest.paths import ALIAS_PATH


@dataclass(frozen=True)
class AliasMap:
    mapping: Dict[str, str]

    def resolve(self, name: str) -> str:
        return self.mapping.get(name, name)


def load_alias_map(csv_path: str | Path = ALIAS_PATH) -> AliasMap:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"alias csv yok: {path}")
    mapping: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or set(reader.fieldnames) != {
            "alias",
            "canonical_name",
        }:
            raise ValueError(
                "alias_mapping.csv başlıkları 'alias,canonical_name' olmalı"
            )
        for i, row in enumerate(reader, start=2):
            alias = row["alias"].strip()
            canonical = row["canonical_name"].strip()
            key = alias
            if key in mapping and mapping[key] != canonical:
                raise ValueError(
                    f"alias çakışması satır {i}: {alias} -> {mapping[key]} / {canonical}"
                )
            mapping[key] = canonical
    return AliasMap(mapping)
