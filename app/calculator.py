"""CLI calculator: evaluates arithmetic expressions without eval() or exec()."""

from __future__ import annotations

import ast
import operator
import sys
from typing import Any


_ALLOWED_BINOPS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARYOPS: dict[type[ast.unaryop], Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_expression(expr: str) -> int | float:
    """Parse and evaluate a numeric arithmetic expression safely."""
    tree = ast.parse(expr.strip(), mode="eval")
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, bool):
            raise ValueError(f"disallowed constant: {v!r}")
        if isinstance(v, (int, float)):
            return v
        raise ValueError(f"disallowed constant: {v!r}")

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        fn = _ALLOWED_UNARYOPS[type(node.op)]
        return fn(_eval_node(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        fn = _ALLOWED_BINOPS[type(node.op)]
        return fn(_eval_node(node.left), _eval_node(node.right))

    raise ValueError(f"disallowed expression: {ast.dump(node, annotate_fields=False)}")


def main() -> None:
    if sys.stdin.isatty():
        raw = input("Expression: ").strip()
    else:
        raw = sys.stdin.read().strip()

    if not raw:
        print("Error: empty expression", file=sys.stderr)
        sys.exit(1)

    try:
        result = evaluate_expression(raw)
    except (SyntaxError, ValueError, ZeroDivisionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result)


if __name__ == "__main__":
    main()
