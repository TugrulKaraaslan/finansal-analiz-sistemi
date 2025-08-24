from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
FILTERS_CSV = ROOT / "filters.csv"


def _load_canonical_filters(path: Path = FILTERS_CSV) -> set[str]:
    """Load canonical filter codes from filters.csv.

    The repository uses a canonical-only policy for filter identifiers. This
    helper reads `filters.csv` which is expected to use `;` as separator with
    a `FilterCode` column. Only the codes are returned.
    """
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        return {row["FilterCode"] for row in reader if row.get("FilterCode")}


@dataclass
class StrategySpec:
    """Specification for a backtest strategy."""

    id: str
    filters: List[str] = field(default_factory=list)
    params: Dict[str, object] = field(default_factory=dict)


class StrategyRegistry:
    """Registry holding available strategies.

    A minimal in-memory registry that can also be constructed from YAML or
    JSON files. During registration filter names are validated against the
    canonical list loaded from :mod:`filters.csv`.
    """

    def __init__(self) -> None:
        self._strategies: Dict[str, StrategySpec] = {}
        self._canonical_filters = _load_canonical_filters()

    # ------------------------------------------------------------------
    def register(self, spec: StrategySpec) -> None:
        """Register a new strategy specification.

        Raises:
            ValueError: If the strategy id already exists or the filters are
                not canonical.
        """

        if spec.id in self._strategies:
            raise ValueError(f"strategy already exists: {spec.id}")
        unknown = [f for f in spec.filters if f not in self._canonical_filters]
        if unknown:
            raise ValueError(f"unknown filters: {', '.join(unknown)}")
        self._strategies[spec.id] = spec

    # ------------------------------------------------------------------
    def get(self, strategy_id: str) -> StrategySpec:
        return self._strategies[strategy_id]

    # ------------------------------------------------------------------
    @classmethod
    def load_from_file(cls, path: str | Path) -> Tuple["StrategyRegistry", Dict[str, object]]:
        """Load strategies and optional constraints from YAML/JSON file.

        The file format is expected to be of the form::

            strategies:
              - id: foo
                filters: ["T1", "T2"]
                params: {risk: 10}
            constraints:
              maxdd_pct: 25

        Returns a tuple of (registry, constraints_dict).
        """

        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            if path.suffix in {".yaml", ".yml"}:
                cfg = yaml.safe_load(f) or {}
            else:
                cfg = json.load(f)
        registry = cls()
        for item in cfg.get("strategies", []):
            spec = StrategySpec(
                id=item["id"],
                filters=item.get("filters", []),
                params=item.get("params", {}),
            )
            registry.register(spec)
        constraints = cfg.get("constraints", {})
        return registry, constraints

    # ------------------------------------------------------------------
    def save(self, path: str | Path) -> None:
        """Persist registry into YAML file."""

        path = Path(path)
        data = {
            "strategies": [
                {"id": s.id, "filters": s.filters, "params": s.params}
                for s in self._strategies.values()
            ]
        }
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
