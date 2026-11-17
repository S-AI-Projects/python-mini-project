import builtins
import importlib.util
from pathlib import Path

import pytest


_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Complete-Calculus-Engine"
    / "Complete-Calculus-Engine.py"
)


@pytest.fixture
def parse_polynomial(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *args, **kwargs: "")
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: None)
    spec = importlib.util.spec_from_file_location("complete_calculus_engine", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_polynomial


def test_parse_polynomial_returns_terms_in_descending_power_order(parse_polynomial):
    assert parse_polynomial("3x^2 - x^-1 + 5") == [
        {"coeff": 3.0, "power": 2, "is_ln": False},
        {"coeff": 5.0, "power": 0, "is_ln": False},
        {"coeff": -1.0, "power": -1, "is_ln": False},
    ]


def test_parse_polynomial_combines_like_terms(parse_polynomial):
    assert parse_polynomial("2x + 3 - x") == [
        {"coeff": 1.0, "power": 1, "is_ln": False},
        {"coeff": 3.0, "power": 0, "is_ln": False},
    ]


def test_parse_polynomial_returns_none_for_empty_input(parse_polynomial):
    assert parse_polynomial("") is None


@pytest.mark.parametrize("expression", ["x + 2y", "x +", "2**x"])
def test_parse_polynomial_rejects_unparsed_input(parse_polynomial, expression):
    assert parse_polynomial(expression) is None
