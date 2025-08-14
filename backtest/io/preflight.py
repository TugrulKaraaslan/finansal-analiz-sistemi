from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, List
from difflib import get_close_matches

from utils.paths import resolve_path


@dataclass
class PreflightReport:
    """Results of running a preflight check over expected Excel files."""

    searched_dir: Path
    glob_pattern: str
    found_files: List[Path] = field(default_factory=list)
    missing_dates: List[date] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def preflight(
    excel_dir: Path | str,
    date_range: Iterable[date],
    pattern: str,
    *,
    date_format: str = "%Y-%m-%d",
    case_sensitive: bool = True,
) -> PreflightReport:
    """Check that expected Excel files exist before scanning.

    Parameters
    ----------
    excel_dir:
        Directory that should contain Excel files.
    date_range:
        Iterable of :class:`datetime.date` objects to check.
    pattern:
        Filename pattern that includes ``{date}`` placeholder.
    date_format:
        ``strftime`` format used for ``date`` substitution.
    case_sensitive:
        Whether filename matching should be case-sensitive.
    """

    dates = list(date_range)
    searched_dir = resolve_path(excel_dir)
    report = PreflightReport(
        searched_dir=searched_dir,
        glob_pattern=pattern.replace("{date}", "*"),
    )

    if not searched_dir.exists():
        report.errors.append(f"Excel klasörü bulunamadı: {searched_dir}")
        parent = searched_dir.parent
        if parent.exists():
            cand = [
                p.name
                for p in parent.iterdir()
                if p.is_dir() and p.name.lower() == searched_dir.name.lower()
            ]
            for c in cand:
                if c != searched_dir.name:
                    report.suggestions.append(
                        (
                            f"Klasörü '{c}/' altında buldum. "
                            f"Config'te 'excel_dir: {c}' yapmayı dener misin?"
                        )
                    )
        return report

    files_in_dir = {p.name: p for p in searched_dir.iterdir() if p.is_file()}
    lower_map = {name.lower(): p for name, p in files_in_dir.items()}

    for d in dates:
        ds = d.strftime(date_format)
        expected = pattern.format(date=ds)
        if case_sensitive:
            fp = files_in_dir.get(expected)
        else:
            fp = lower_map.get(expected.lower())
        if fp:
            report.found_files.append(fp)
            continue
        report.missing_dates.append(d)
        # suggestions based on near matches
        near = get_close_matches(
            expected if case_sensitive else expected.lower(),
            list(files_in_dir.keys() if case_sensitive else lower_map.keys()),
            n=3,
            cutoff=0.6,
        )
        for n in near:
            # if case insensitive, 'n' may be lower-case key
            sug = files_in_dir.get(n) or lower_map.get(n)
            if sug:
                report.suggestions.append(f"Benzer dosya: {sug.name}")

    if report.missing_dates:
        miss = ", ".join(d.strftime("%Y-%m-%d") for d in report.missing_dates)
        report.warnings.append(f"Eksik dosyalar: {miss}")

    return report


__all__ = ["PreflightReport", "preflight"]
