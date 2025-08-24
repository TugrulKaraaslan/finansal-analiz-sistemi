from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeReport:
    mapping: Dict[str, str] = field(default_factory=dict)
    collisions: list[dict] = field(default_factory=list)  # {canonical, originals}
    dropped: list[str] = field(default_factory=list)
    renamed: list[str] = field(default_factory=list)

    def add_collision(self, canonical: str, originals: list[str]):
        self.collisions.append({"canonical": canonical, "originals": originals})

    def add_rename(self, old: str, new: str):
        self.renamed.append(f"{old}->{new}")
