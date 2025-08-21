from __future__ import annotations

import ast
import re
from typing import Any, Callable, Dict

import pandas as pd
from loguru import logger

from .columns import ALIASES, canonicalize
from .cross import cross_down, cross_up


ALLOWED_FUNCS: Dict[str, Callable[[pd.Series, pd.Series], pd.Series]] = {
    "CROSSUP": cross_up,
    "CROSSDOWN": cross_down,
    "CROSS_UP": cross_up,
    "CROSS_DOWN": cross_down,
}

COMPARATORS: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Gt: lambda a, b: a > b,
    ast.Lt: lambda a, b: a < b,
    ast.GtE: lambda a, b: a >= b,
    ast.LtE: lambda a, b: a <= b,
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
}


def _canon(name: str) -> str:
    can = canonicalize(name)
    return ALIASES.get(can, can)


def _ensure_series(value: Any, index: pd.Index) -> pd.Series:
    if isinstance(value, pd.Series):
        return value
    if isinstance(value, pd.DataFrame):
        if value.shape[1] == 1:
            return value.iloc[:, 0]
        return value.any(axis=1)
    return pd.Series(value, index=index)


def _preprocess(expr: str) -> str:
    expr = re.sub(r"\bAND\b", "&", expr, flags=re.I)
    expr = re.sub(r"\bOR\b", "|", expr, flags=re.I)
    expr = re.sub(r"\bNOT\b", "~", expr, flags=re.I)
    return expr


def evaluate(df: pd.DataFrame, expr: str) -> pd.Series:
    expr = _preprocess(expr)
    tree = ast.parse(expr, mode="eval")

    func_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    column_names = {n for n in names if n not in func_names}
    resolved = {_canon(n) for n in column_names}
    for name in resolved:
        if "_1h_" in name:
            logger.warning("intraday filtre çıkarıldı")
            return pd.Series(True, index=df.index)
        if name not in df.columns:
            raise KeyError(f"Column {name!r} not found in DataFrame")

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.BitAnd):
                return _ensure_series(left, df.index) & _ensure_series(right, df.index)
            if isinstance(node.op, ast.BitOr):
                return _ensure_series(left, df.index) | _ensure_series(right, df.index)
            raise SyntaxError("Unsupported binary operator")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            return ~_ensure_series(_eval(node.operand), df.index)
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            result = pd.Series(True, index=df.index)
            for op, comp in zip(node.ops, node.comparators):
                right = _eval(comp)
                op_type = type(op)
                if op_type not in COMPARATORS:
                    raise SyntaxError("Unsupported comparison operator")
                result &= COMPARATORS[op_type](
                    _ensure_series(left, df.index),
                    _ensure_series(right, df.index),
                )
                left = right
            return result
        if isinstance(node, ast.Name):
            name = _canon(node.id)
            return _ensure_series(df[name], df.index)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            func_name = node.func.id.upper()
            if func_name not in ALLOWED_FUNCS:
                raise SyntaxError(f"Function {func_name!r} not allowed")
            if len(node.args) != 2:
                raise SyntaxError("Functions expect exactly two arguments")
            arg1 = _ensure_series(_eval(node.args[0]), df.index)
            arg2 = _ensure_series(_eval(node.args[1]), df.index)
            return ALLOWED_FUNCS[func_name](arg1, arg2)
        raise SyntaxError("Unsupported expression element")

    result = _ensure_series(_eval(tree), df.index)
    if not pd.api.types.is_bool_dtype(result):
        raise ValueError("Expression must evaluate to boolean mask")
    return result


__all__ = ["evaluate"]
