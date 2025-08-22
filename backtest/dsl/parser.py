from __future__ import annotations
import ast
from .errors import DSLParseError, DSLForbiddenNode

# Whitelist edilen node tipleri
_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Call,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Gt,
    ast.Lt,
    ast.GtE,
    ast.LtE,
    ast.Eq,
    ast.NotEq,
)
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)
_ALLOWED_UNARY = (ast.Not, ast.USub, ast.UAdd)
_ALLOWED_CMPS = (ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq)
_ALLOWED_BOOLOPS = (ast.And, ast.Or)


def _check_whitelist(node: ast.AST) -> None:
    if not isinstance(node, _ALLOWED_NODES):
        raise DSLForbiddenNode(f"Yasak AST düğümü: {type(node).__name__}", code="DF002")
    for child in ast.iter_child_nodes(node):
        if isinstance(node, ast.BinOp) and not isinstance(node.op, _ALLOWED_BINOPS):
            raise DSLForbiddenNode("Yasak BinOp", code="DF002")
        if isinstance(node, ast.UnaryOp) and not isinstance(node.op, _ALLOWED_UNARY):
            raise DSLForbiddenNode("Yasak UnaryOp", code="DF002")
        if isinstance(node, ast.BoolOp) and not isinstance(node.op, _ALLOWED_BOOLOPS):
            raise DSLForbiddenNode("Yasak BoolOp", code="DF002")
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if not isinstance(op, _ALLOWED_CMPS):
                    raise DSLForbiddenNode("Yasak Compare op", code="DF002")
        _check_whitelist(child)


def parse_expression(expr: str) -> ast.Expression:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise DSLParseError(f"Sözdizimi hatası: {e}", code="DF001") from e
    _check_whitelist(tree)
    return tree
