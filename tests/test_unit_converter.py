"""Regression tests for utilities/Unit-Converter/main.py."""

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Unit-Converter"
    / "main.py"
)


@pytest.fixture(scope="module")
def converter():
    spec = importlib.util.spec_from_file_location("unit_converter", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        (1, "km", "m", 1000),
        (100, "cm", "m", 1),
        (1, "m", "ft", 3.280839895013123),
        (1, "kg", "lb", 2.2046226218487757),
        (16, "oz", "lb", 1),
        (0, "C", "C", 0),
        (32, "F", "C", 0),
        (273.15, "K", "C", 0),
    ],
)
def test_conversions(converter, value, from_unit, to_unit, expected):
    assert converter.convert(value, from_unit, to_unit) == pytest.approx(expected)


def test_celsius_identity_is_preserved(converter):
    assert converter.convert_temperature(25, "C", "C") == 25


def test_temperature_mutant_is_rejected_by_identity_case(converter):
    # This test documents the decisive Celsius branch: a mutation that
    # changes the Celsius identity condition must fail with 25 != 298.15.
    assert converter.convert_temperature(25, "C", "C") == 25


@pytest.mark.parametrize(
    ("function_name", "args"),
    [
        ("convert_length", (1, "meter", "parsec")),
        ("convert_weight", (1, "stone", "kg")),
        ("convert_temperature", (1, "rankine", "C")),
    ],
)
def test_unsupported_units_raise(converter, function_name, args):
    with pytest.raises(ValueError):
        getattr(converter, function_name)(*args)
