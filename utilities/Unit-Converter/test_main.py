"""Unittest checks for utilities/Unit-Converter/main.py."""

import importlib.util
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO


MODULE_PATH = Path(__file__).with_name("main.py")
WORK_PATH = Path(__file__).resolve().parents[2] / "work" / "R26-T030"
RESULTS_PATH = WORK_PATH / "case-results.jsonl"
WORK_PATH.mkdir(parents=True, exist_ok=True)

SPEC = importlib.util.spec_from_file_location("unit_converter", MODULE_PATH)
CONVERTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONVERTER)


class UnitConverterTests(unittest.TestCase):
    def record(self, name, inputs, expected, actual, passed):
        record = {
            "check": name,
            "inputs": inputs,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }
        with RESULTS_PATH.open("a", encoding="utf-8") as result_file:
            result_file.write(json.dumps(record, sort_keys=True) + "\n")

    def assert_close_conversion(self, name, value, from_unit, to_unit, expected):
        actual = CONVERTER.convert(value, from_unit, to_unit)
        tolerance = 1e-9
        passed = math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)
        inputs = {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
        }
        self.record(name, inputs, expected, actual, passed)
        self.assertTrue(passed)

    def test_supported_conversions(self):
        cases = [
            ("kilometers_to_meters", 1, "kilometer", "meter", 1000),
            ("centimeters_to_meters", 100, "cm", "m", 1),
            ("inches_to_feet", 12, "in", "ft", 1),
            ("kilograms_to_grams", 1, "kg", "g", 1000),
            ("ounces_to_pounds", 16, "oz", "lb", 1),
            ("celsius_to_fahrenheit", 0, "C", "F", 32),
            ("fahrenheit_to_celsius", 32, "F", "C", 0),
            ("kelvin_to_celsius", 273.15, "K", "C", 0),
        ]
        for case in cases:
            with self.subTest(check=case[0]):
                self.assert_close_conversion(*case)

    def test_celsius_identity(self):
        actual = CONVERTER.convert_temperature(25, "C", "C")
        passed = actual == 25
        inputs = {"value": 25, "from_unit": "C", "to_unit": "C"}
        self.record("celsius_identity", inputs, 25, actual, passed)
        self.assertEqual(actual, 25)

    def test_unsupported_units(self):
        cases = [
            ("length", CONVERTER.convert_length, (1, "meter", "parsec")),
            ("weight", CONVERTER.convert_weight, (1, "stone", "kg")),
            ("temperature", CONVERTER.convert_temperature, (1, "rankine", "C")),
        ]
        for name, function, arguments in cases:
            with self.subTest(unit_type=name):
                try:
                    function(*arguments)
                    actual = "no exception"
                except ValueError as error:
                    actual = str(error)
                    passed = True
                    self.record(
                        "unsupported_" + name,
                        {"arguments": list(arguments)},
                        "ValueError",
                        actual,
                        passed,
                    )
                    self.assertRaises(ValueError, function, *arguments)
                    continue
                passed = False
                self.record(
                    "unsupported_" + name,
                    {"arguments": list(arguments)},
                    "ValueError",
                    actual,
                    passed,
                )
                self.fail("unsupported unit did not raise ValueError")

    def test_incompatible_units(self):
        try:
            CONVERTER.convert_units(1, "meter", "kg")
            actual = "no exception"
            passed = False
        except ValueError as error:
            actual = str(error)
            passed = "unsupported or incompatible" in actual
        inputs = {"value": 1, "from_unit": "meter", "to_unit": "kg"}
        self.record("incompatible_units", inputs, "ValueError", actual, passed)
        with self.assertRaises(ValueError):
            CONVERTER.convert_units(1, "meter", "kg")

    def test_non_numeric_values_are_rejected(self):
        try:
            CONVERTER.convert_length("one", "m", "cm")
            actual = "no exception"
            passed = False
        except TypeError as error:
            actual = str(error)
            passed = True
        inputs = {"value": "one", "from_unit": "m", "to_unit": "cm"}
        self.record("non_numeric_value", inputs, "TypeError", actual, passed)
        with self.assertRaises(TypeError):
            CONVERTER.convert_length("one", "m", "cm")

    def test_below_absolute_zero_is_rejected(self):
        try:
            CONVERTER.convert_temperature(-1, "K", "C")
            actual = "no exception"
            passed = False
        except ValueError as error:
            actual = str(error)
            passed = "absolute zero" in actual
        inputs = {"value": -1, "from_unit": "K", "to_unit": "C"}
        self.record("below_absolute_zero", inputs, "ValueError", actual, passed)
        with self.assertRaises(ValueError):
            CONVERTER.convert_temperature(-1, "K", "C")

    def test_non_finite_values_are_rejected(self):
        for bad_value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=bad_value):
                try:
                    CONVERTER.convert_units(bad_value, "m", "cm")
                    actual = "no exception"
                    passed = False
                except ValueError as error:
                    actual = str(error)
                    passed = "finite" in actual
                inputs = {"value": repr(bad_value), "from_unit": "m", "to_unit": "cm"}
                self.record("non_finite_value", inputs, "ValueError", actual, passed)
                with self.assertRaises(ValueError):
                    CONVERTER.convert_units(bad_value, "m", "cm")

    def test_cli_length_example(self):
        output = StringIO()
        supplied = ["1", "100", "cm", "m", "4"]
        with patch("builtins.input", side_effect=supplied), patch("sys.stdout", output):
            CONVERTER.main()
        text = output.getvalue()
        passed = "100.0 cm = 1.0 m" in text
        inputs = {"menu_choice": "1", "value": "100", "from_unit": "cm", "to_unit": "m", "exit": "4"}
        self.record("cli_length_example", inputs, "Result: 100.0 cm = 1.0 m", text, passed)
        self.assertIn("100.0 cm = 1.0 m", text)


if __name__ == "__main__":
    unittest.main()
