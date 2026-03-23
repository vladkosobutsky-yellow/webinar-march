"""CLI calculator: evaluates arithmetic expressions without eval() or exec()."""

from __future__ import annotations

import ast
import sys
from collections.abc import Callable


def _apply_uadd(x: int | float) -> int | float:
    return +x


def _apply_usub(x: int | float) -> int | float:
    return -x


def _apply_add(a: int | float, b: int | float) -> int | float:
    return a + b


def _apply_sub(a: int | float, b: int | float) -> int | float:
    return a - b


def _apply_mul(a: int | float, b: int | float) -> int | float:
    return a * b


def _apply_truediv(a: int | float, b: int | float) -> int | float:
    return a / b


def _apply_floordiv(a: int | float, b: int | float) -> int | float:
    return a // b


def _apply_mod(a: int | float, b: int | float) -> int | float:
    return a % b


def _apply_pow(a: int | float, b: int | float) -> int | float:
    return a**b


_ALLOWED_UNARYOPS: dict[type[ast.unaryop], Callable[[int | float], int | float]] = {
    ast.UAdd: _apply_uadd,
    ast.USub: _apply_usub,
}

_ALLOWED_BINOPS: dict[type[ast.operator], Callable[[int | float, int | float], int | float]] = {
    ast.Add: _apply_add,
    ast.Sub: _apply_sub,
    ast.Mult: _apply_mul,
    ast.Div: _apply_truediv,
    ast.FloorDiv: _apply_floordiv,
    ast.Pow: _apply_pow,
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


def main() -> None:  # pragma: no cover
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


if __name__ == "__main__":  # pragma: no cover
    main()
