from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Flags:
    dry_run: bool = True
    filters_enabled: bool = True
    write_outputs: bool = True

    @classmethod
    def from_dict(cls, d: dict) -> "Flags":
        return cls(
            dry_run=bool(d.get("dry_run", True)),
            filters_enabled=bool(d.get("filters_enabled", True)),
            write_outputs=bool(d.get("write_outputs", True)),
        )
