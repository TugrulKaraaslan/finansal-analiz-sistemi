#!/usr/bin/env python3
"""Normalize crossover function names in CSV/DSL files.

Usage:
    python tools/migrate_cross_aliases.py input.csv output.csv

Replaces legacy crossover function names like ``CROSSUP`` or ``crossOver``
with the canonical ``cross_up`` / ``cross_down`` equivalents.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ALIASES = [
    (r"\b(CROSSUP|crossUp|CROSS_UP|crossOver|cross_over|keser_yukari|kesisim_yukari)\s*\(", "cross_up("),
    (r"\b(CROSSDOWN|crossDown|CROSS_DOWN|crossUnder|cross_under|keser_asagi|kesisim_asagi)\s*\(", "cross_down("),
]


def _normalize(text: str) -> str:
    for pat, repl in _ALIASES:
        text = re.sub(pat, repl, text, flags=re.I)
    # handle Turkish macro forms ``X_keser_Y_yukari`` etc.
    text = re.sub(
        r"([A-Za-z0-9_]+)_keser_([A-Za-z0-9_]+)_yukari",
        r"cross_up(\1,\2)",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"([A-Za-z0-9_]+)_keser_([A-Za-z0-9_]+)_asagi",
        r"cross_down(\1,\2)",
        text,
        flags=re.I,
    )
    return text


def main() -> None:
    if len(sys.argv) != 3:
        print("usage: python tools/migrate_cross_aliases.py input.csv output.csv")
        raise SystemExit(1)
    src, dst = sys.argv[1], sys.argv[2]
    data = Path(src).read_text()
    Path(dst).write_text(_normalize(data))


if __name__ == "__main__":
    main()
