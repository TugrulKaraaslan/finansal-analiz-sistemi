from __future__ import annotations

import ast
import operator as op
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .errors import DSLBadArgs, DSLUnknownName
from .functions import FUNCTIONS
from .parser import parse_expression

# Karşılaştırma ve aritmetik operatörleri vektörel uygular
_ARITH = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
}
_CMPOP = {
    ast.Gt: op.gt,
    ast.Lt: op.lt,
    ast.GtE: op.ge,
    ast.LtE: op.le,
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
}


class SeriesContext:
    """İsim→seri/skaler sözlüğü sağlayan bağlam.
    Değer dönerken pandas.Series ya da skaler (int/float) dönebilir.
    """

    def __init__(self, values: Mapping[str, Any]):
        self.values = values

    def get(self, name: str):
        if name not in self.values:
            raise DSLUnknownName(f"Tanımsız isim: {name}", code="DF003")
        return self.values[name]


class Evaluator:
    def __init__(self, context: SeriesContext):
        self.ctx = context

    def eval(self, expr: str) -> pd.Series:
        tree = parse_expression(expr)
        res = self._eval_node(tree.body)
        # Bool dtype garanti et; NaN→False
        if isinstance(res, pd.Series):
            if res.dtype != bool:
                # Karşılaştırma dışındaki aritmetik sonuçlarını bool'e çevirmek istemeyiz;
                # DSL'de üst düzey sonuç bool olmalı. 0/NaN → False, diğer → True kuralı uygulanır.
                res = res.astype(float).fillna(0.0) != 0.0
            return res.fillna(False)
        if isinstance(res, (int, float, bool)):
            return pd.Series(bool(res))  # tek değerli
        raise TypeError("Beklenmeyen eval sonucu")

    def _eval_node(self, node):
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return _ARITH[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.Not):
                return (~operand).fillna(False) if isinstance(operand, pd.Series) else (not operand)
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return +operand
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                out = self._eval_node(node.values[0])
                for v in node.values[1:]:
                    self._eval_node(v)  # yan etkiler/isim kontrolü
                return out
            if isinstance(node.op, ast.Or):
                vals = [self._eval_node(v) for v in node.values]
                out = vals[0]
                for v in vals[1:]:
                    out = (out | v) if isinstance(out, pd.Series) else (bool(out) or bool(v))
                return out
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            result = None
            for op_node, comp in zip(node.ops, node.comparators):
                right = self._eval_node(comp)
                cmp_func = _CMPOP[type(op_node)]
                chunk = cmp_func(left, right)
                if isinstance(chunk, pd.Series):
                    chunk = chunk.fillna(False)
                result = chunk if result is None else (result & chunk)
                left = right
            return result
        if isinstance(node, ast.Name):
            return self.ctx.get(node.id)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "id", None)
            if func_name not in FUNCTIONS:
                raise DSLUnknownName(f"Tanımsız fonksiyon: {func_name}", code="DF003")
            fn = FUNCTIONS[func_name]
            args = [self._eval_node(a) for a in node.args]
            try:
                return fn(*args)
            except TypeError as e:
                raise DSLBadArgs(str(e), code="DF004") from e
        raise TypeError(f"Beklenmeyen AST düğümü: {type(node).__name__}")
