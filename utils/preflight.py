import re
import pandas as pd

REQUIRED_COLUMNS = ["sma_10", "sma_50", "adx_14"]
TARGET_DATE = "2025-03-07"


def smart_parse_dates(series: pd.Series) -> pd.Series:
    """Safely parse date strings in ISO (YYYY-MM-DD) or Turkish (DD.MM.YYYY) format.

    The function automatically detects ISO formatted strings and parses them
    using the fixed ``%Y-%m-%d`` pattern. Remaining values are parsed with
    ``dayfirst=True`` to support common local formats like ``07.03.2025`` or
    ``07/03/2025``. Any unparsable values result in ``NaT``.
    """
    series = series.astype(str).str.strip()

    # Identify ISO ``YYYY-MM-DD`` strings
    iso_mask = series.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    iso = pd.to_datetime(series.where(iso_mask), errors="coerce", format="%Y-%m-%d")

    # Remaining values are treated as day-first (Turkish style)
    local = pd.to_datetime(series.where(~iso_mask), errors="coerce", dayfirst=True)

    return iso.combine_first(local)


def canonical(col: str) -> str:
    """Return a normalized representation of a column name."""
    s = str(col).strip().lower()
    tr = {
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ş": "s",
        "ö": "o",
        "ç": "c",
        "İ": "i",
        "Ğ": "g",
        "Ü": "u",
        "Ş": "s",
        "Ö": "o",
        "Ç": "c",
    }
    for k, v in tr.items():
        s = s.replace(k, v)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def preflight_check(df: pd.DataFrame, target_date: str = TARGET_DATE) -> dict:
    """Find target date rows and report missing core columns."""
    date_col = df.columns[0]  # assume first column stores dates
    dser = smart_parse_dates(df[date_col])
    mask = dser.dt.normalize() == pd.to_datetime(target_date)

    canon_cols = {canonical(c) for c in df.columns}
    missing = [c for c in REQUIRED_COLUMNS if c not in canon_cols]

    return {"rows_on_target": int(mask.sum()), "missing_required_cols": missing}


__all__ = [
    "smart_parse_dates",
    "canonical",
    "preflight_check",
    "REQUIRED_COLUMNS",
    "TARGET_DATE",
]
