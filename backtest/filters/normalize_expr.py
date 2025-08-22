from __future__ import annotations

import io
import re
import tokenize


_LOGICAL = {"and": "&", "or": "|"}
_COMPARATORS = {"<", ">", "<=", ">=", "==", "!="}


def _collapse_underscores(s: str) -> str:
    return re.sub(r"__+", "_", s)


def normalize_expr(expr: str) -> str:
    """Normalise a filter expression string.

    * Convert logical operators ``and``/``or`` to ``&``/``|``
      while preserving string literals.
    * Fix common StochRSI token typos.
    * Remove stray decimal fragments like ``name .015`` that may appear
      before a comparison operator.
    * Collapse multiple underscores.
    """

    tokens = list(tokenize.generate_tokens(io.StringIO(expr).readline))
    out_tokens: list[tokenize.TokenInfo] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type == tokenize.NAME:
            val = tok.string
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
                tok = tok._replace(
                    string=tok.string
                    + tokens[i + 1].string
                    + tokens[i + 2].string
                )
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
    normalised = _collapse_underscores(normalised)
    normalised = re.sub(r"\s+(?=[<>]=?|==|!=)", " ", normalised)
    normalised = re.sub(r"\s+\)", ")", normalised)
    normalised = re.sub(r"\s+,", ",", normalised)
    return normalised


__all__ = ["normalize_expr"]
