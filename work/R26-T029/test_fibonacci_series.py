import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "math" / "Fibonacci-Series" / "Fibonacci-Series.py"


def load_named_module():
    turtle = ModuleType("turtle")
    with patch.dict(sys.modules, {"turtle": turtle}):
        spec = importlib.util.spec_from_file_location("fibonacci_series_named_module", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    return module


fibonacci_module = load_named_module()
generate_fibonacci = fibonacci_module.generate_fibonacci


def test_zero_and_negative_term_counts():
    assert generate_fibonacci(0) == []
    assert generate_fibonacci(-3) == []


def test_one_and_two_terms():
    assert generate_fibonacci(1) == [1]
    assert generate_fibonacci(2) == [1, 1]


def test_sequence_and_length():
    result = generate_fibonacci(10)

    assert len(result) == 10
    assert result == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    assert all(result[i] == result[i - 1] + result[i - 2] for i in range(2, len(result)))


def test_large_sequence_output():
    result = generate_fibonacci(100)

    assert len(result) == 100
    assert all(result[i] == result[i - 1] + result[i - 2] for i in range(2, 100))
