from __future__ import annotations

import ast
from typing import Any, Callable, Dict

from pyecore.ecore import EObject


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Dict,
    ast.Subscript,
)

_INDEX_NODE = getattr(ast, "Index", None)
_SLICE_NODE = getattr(ast, "Slice", None)
if _INDEX_NODE is not None:
    _ALLOWED_NODES += (_INDEX_NODE,)
if _SLICE_NODE is not None:
    _ALLOWED_NODES += (_SLICE_NODE,)

_ALLOWED_OPS = (
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)


def _json_safe(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    name = getattr(value, "name", None)
    if name is not None:
        return name
    return str(value)


def _all_features(obj: EObject, name: str):
    attr = getattr(obj.eClass, name, [])
    return attr() if callable(attr) else list(attr)


def build_context(obj: EObject, obj_id: str, path: str) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}
    for attr in _all_features(obj, "eAllAttributes"):
        value = obj.eGet(attr)
        if attr.many:
            attrs[attr.name] = _json_safe(list(value)) if value is not None else []
        else:
            attrs[attr.name] = _json_safe(value)
    ctx: Dict[str, Any] = {
        "eclass": obj.eClass.name,
        "nsuri": obj.eClass.ePackage.nsURI if obj.eClass.ePackage else None,
        "id": obj_id,
        "path": path,
        "attrs": attrs,
    }
    ctx.update(attrs)
    return ctx


def _validate_expr(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES + _ALLOWED_OPS):
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Invalid name in expression")


def build_predicate(expr: str) -> Callable[[Dict[str, Any]], bool]:
    tree = ast.parse(expr, mode="eval")
    _validate_expr(tree)
    code = compile(tree, "<filter>", "eval")

    def predicate(ctx: Dict[str, Any]) -> bool:
        return bool(eval(code, {"__builtins__": {}}, ctx))

    return predicate
