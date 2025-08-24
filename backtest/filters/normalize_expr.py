from __future__ import annotations

import io
import re
import tokenize
from typing import List, Tuple


_LOGICAL = {"and": "&", "or": "|"}

# canonical function name mapping
_FUNC_MAP = {
    # cross up variations
    "crossup": "cross_up",
    "cross_up": "cross_up",
    "crossover": "cross_up",
    "cross_over": "cross_up",
    "keser_yukari": "cross_up",
    "kesisim_yukari": "cross_up",
    # cross down variations
    "crossdown": "cross_down",
    "cross_down": "cross_down",
    "crossunder": "cross_down",
    "cross_under": "cross_down",
    "keser_asagi": "cross_down",
    "kesisim_asagi": "cross_down",
}


def _collapse_underscores(s: str) -> str:
    return re.sub(r"__+", "_", s)


def normalize_expr(expr: str) -> Tuple[str, List[Tuple[str, str, str]]]:
    """Normalise a filter expression string.

    * Convert logical operators ``and``/``or`` to ``&``/``|``
      while preserving string literals.
    * Fix common StochRSI token typos and ``cci_*_0`` tokens.
    * Remove stray decimal fragments like ``name .015`` that may appear
      before a comparison operator.
    * Collapse multiple underscores.
    * Detect ``cross_up``/``cross_down`` macros and return them separately.
    """

    tokens = list(tokenize.generate_tokens(io.StringIO(expr).readline))
    out_tokens: list[tokenize.TokenInfo] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == tokenize.NAME:
            val = tok.string.lower()
            # logical ops
            if val in _LOGICAL:
                new_tok = tokenize.TokenInfo(
                    type=tokenize.OP,
                    string=_LOGICAL[val],
                    start=tok.start,
                    end=tok.end,
                    line=tok.line,
                )
                out_tokens.append(new_tok)
                i += 1
                continue
            # stochrsi typos
            if val.startswith("stochrsik_"):
                val = val.replace("stochrsik_", "stochrsi_k_")
            elif val.startswith("stochrsid_"):
                val = val.replace("stochrsid_", "stochrsi_d_")
            tok = tok._replace(string=val)
            out_tokens.append(tok)
            # handle trailing decimal fragments
            if (
                i + 2 < len(tokens)
                and tokens[i + 1].type == tokenize.NUMBER
                and tokens[i + 1].string.startswith(".")
                and "_" in tokens[i + 1].string
                and tokens[i + 2].type == tokenize.NUMBER
                and tokens[i + 2].string.startswith(".")
            ):
                concat = tok.string + tokens[i + 1].string
                concat += tokens[i + 2].string
                tok = tok._replace(string=concat)
                out_tokens[-1] = tok
                i += 3
                continue
            if (
                i + 1 < len(tokens)
                and tokens[i + 1].type == tokenize.NUMBER
                and tokens[i + 1].string.startswith(".")
            ):
                i += 2
                continue
        else:
            out_tokens.append(tok)
        i += 1

    normalised = tokenize.untokenize(out_tokens)
    normalised = re.sub(r"\bpsarl_0\.0?2_0\.2\b", "psarl_0_02_0_2", normalised, flags=re.I)
    normalised = re.sub(r"(?<![A-Za-z0-9_])_(100|80|70|50)\b", r"-\1", normalised)
    normalised = re.sub(r"\s=\s=", " == ", normalised)
    normalised = re.sub(r"\s*==\s*", " == ", normalised)
    # alias fixes
    normalised = re.sub(r"cci_(\d+)_0", r"cci_\1", normalised, flags=re.I)
    normalised = _collapse_underscores(normalised)
    normalised = re.sub(r"\s+(?=[<>]=?|==|!=)", " ", normalised)
    normalised = re.sub(r"\s+\)", ")", normalised)
    normalised = re.sub(r"\s+,", ",", normalised)

    # Turkish macro forms
    normalised = re.sub(
        r"([A-Za-z0-9_]+)_keser_([A-Za-z0-9_]+)_yukari",
        r"cross_up(\1,\2)",
        normalised,
        flags=re.I,
    )
    normalised = re.sub(
        r"([A-Za-z0-9_]+)_keser_([A-Za-z0-9_]+)_asagi",
        r"cross_down(\1,\2)",
        normalised,
        flags=re.I,
    )

    # normalize function aliases
    for alias, canon in _FUNC_MAP.items():
        normalised = re.sub(rf"\b{alias}\s*\(", f"{canon}(", normalised, flags=re.I)

    macros: List[Tuple[str, str, str]] = []

    def _macro_repl(m: re.Match) -> str:
        kind = m.group(1).lower()
        a = _collapse_underscores(m.group(2).strip().lower())
        b = _collapse_underscores(m.group(3).strip().lower())
        full = f"cross_{kind}"
        macros.append((full, a, b))
        return f"cross_{kind}({a},{b})"

    normalised = re.sub(
        r"cross_(up|down)\(([^,]+),([^\)]+)\)",
        _macro_repl,
        normalised,
        flags=re.I,
    )

    normalised = normalised.strip()
    normalised = re.sub(r"\s+", " ", normalised)

    return normalised, macros


__all__ = ["normalize_expr"]
