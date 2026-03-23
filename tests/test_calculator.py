import pytest

from app.calculator import evaluate_expression


def test_basic_add_mult() -> None:
    assert evaluate_expression("5 + 8") == 13
    assert evaluate_expression("(5+8)*2") == 26


def test_precedence() -> None:
    assert evaluate_expression("2 + 3 * 4") == 14
    assert evaluate_expression("(2 + 3) * 4") == 20


def test_unary() -> None:
    assert evaluate_expression("-5 + 3") == -2
    assert evaluate_expression("+(4)") == 4


def test_division_and_float() -> None:
    assert evaluate_expression("10 / 4") == 2.5
    assert evaluate_expression("7 // 2") == 3


def test_power() -> None:
    assert evaluate_expression("2 ** 3") == 8


def test_whitespace_stripped() -> None:
    assert evaluate_expression("  ( 1 + 2 ) * 3  ") == 9


def test_disallowed_name() -> None:
    with pytest.raises(ValueError, match="disallowed"):
        evaluate_expression("__import__('os')")


def test_disallowed_bool_constant() -> None:
    with pytest.raises(ValueError, match="disallowed constant"):
        evaluate_expression("True")


def test_subtraction() -> None:
    assert evaluate_expression("10 - 3") == 7


def test_disallowed_string_constant() -> None:
    with pytest.raises(ValueError, match="disallowed constant"):
        evaluate_expression("'hello'")


def test_syntax_error_propagates() -> None:
    with pytest.raises(SyntaxError):
        evaluate_expression("1 +")
