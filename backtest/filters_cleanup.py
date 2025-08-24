from __future__ import annotations

import re

import pandas as pd

CLEANUP_MAP: dict[str, str] = {
    r"^CCI_20_0$": "CCI_20",
    r"^PSARL_0$": "PSARL_0_02_0_2",
    r"^BBM_20_2.*$": "BBM_20_2",
    r"^BBU_20_2.*$": "BBU_20_2",
    r"^AROONU_(\d+)$": r"AROON_UP_\1",
    r"^AROOND_(\d+)$": r"AROON_DOWN_\1",
}

_TOKEN_RE = re.compile(r"[A-Za-z0-9_.-]+")


def normalize_symbol(name: str) -> str:
    """Return a normalized representation of a symbol name."""

    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", name.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.upper()


def apply_alias(name: str) -> str:
    """Apply alias mapping to a normalized name."""

    for pattern, repl in CLEANUP_MAP.items():
        if re.fullmatch(pattern, name):
            return repl
    return name


def clean_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean filter expressions and produce an alias report.

    Parameters
    ----------
    df:
        DataFrame containing at least ``id`` and ``expr`` columns.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        The cleaned DataFrame and a report DataFrame.
    """

    report_rows = []
    df = df.copy()
    mask = df["expr"].str.contains("_1h_", na=False)
    for _, row in df[mask].iterrows():
        report_rows.append(
            {
                "id": row["id"],
                "original": row["expr"],
                "new_symbol": "",
                "status": "intraday_removed",
            }
        )
    df_clean = df[~mask].copy()

    for idx, row in df_clean.iterrows():
        expr = row["expr"]
        tokens = _TOKEN_RE.findall(expr)
        replacements: dict[str, str] = {}
        for token in tokens:
            norm = normalize_symbol(token)
            if not norm:
                report_rows.append(
                    {
                        "id": row["id"],
                        "original": token,
                        "new_symbol": "",
                        "status": "unmatched",
                    }
                )
                continue
            alias = apply_alias(norm)
            if alias != norm:
                report_rows.append(
                    {
                        "id": row["id"],
                        "original": token,
                        "new_symbol": alias,
                        "status": "aliased",
                    }
                )
                replacements[token] = alias
            else:
                replacements[token] = token

        def repl(match: re.Match[str]) -> str:
            tok = match.group(0)
            return replacements.get(tok, tok)

        df_clean.at[idx, "expr"] = _TOKEN_RE.sub(repl, expr)

    report_df = pd.DataFrame(
        report_rows, columns=["id", "original", "new_symbol", "status"]
    )
    return df_clean, report_df


__all__ = [
    "CLEANUP_MAP",
    "normalize_symbol",
    "apply_alias",
    "clean_filters",
]
