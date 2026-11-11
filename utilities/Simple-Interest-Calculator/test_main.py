"""Unit tests for Simple Interest Calculator.
"""

from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from fractions import Fraction
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest

MAIN_PATH = Path(__file__).resolve().parent / "main.py"

# Load the main module dynamically to support directory names with hyphens
spec = importlib.util.spec_from_file_location("simple_interest_main", MAIN_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {MAIN_PATH}")
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

calculate_simple_interest = main_mod.calculate_simple_interest
format_currency = main_mod.format_currency
to_decimal = main_mod.to_decimal


# Reference methods independent of main.py (Condition 1)
def reference_fraction_interest(p: object, r: object, t: object) -> Fraction:
    """Independent reference calculation using exact rational Fraction arithmetic."""
    p_frac = Fraction(str(p))
    r_frac = Fraction(str(r))
    t_frac = Fraction(str(t))
    return (p_frac * r_frac * t_frac) / Fraction(100)


def reference_annual_loop_interest(p: object, r: object, n: int) -> Decimal:
    """Independent reference calculation accumulating interest once per whole year."""
    p_dec = Decimal(str(p))
    r_dec = Decimal(str(r))
    yearly = (p_dec * r_dec) / Decimal("100")
    total = Decimal("0")
    for _ in range(n):
        total += yearly
    return total


class TestSimpleInterestCalculator(unittest.TestCase):
    """Test suite for contract, reference comparisons, inputs, and CLI."""

    def test_contract_standard_example(self) -> None:
        """1000 at 5% for 2 years -> 100."""
        result = calculate_simple_interest(1000, 5, 2)
        self.assertEqual(result, Decimal("100"))
        self.assertIsInstance(result, Decimal)

    def test_contract_zero_years(self) -> None:
        """Zero years -> 0."""
        self.assertEqual(calculate_simple_interest(1000, 5, 0), Decimal("0"))
        self.assertEqual(calculate_simple_interest("2500", "7.5", "0"), Decimal("0"))

    def test_contract_negative_principal_raises_value_error(self) -> None:
        """Negative principal -> ValueError."""
        with self.assertRaises(ValueError):
            calculate_simple_interest(-1000, 5, 2)
        with self.assertRaises(ValueError):
            calculate_simple_interest("-0.01", 5, 2)
        with self.assertRaises(ValueError):
            calculate_simple_interest(Decimal("-1"), 5, 2)

    def test_hand_calculated_table(self) -> None:
        """Verify the 8 required hand-calculated test cases."""
        table = [
            ("1000", "5", "2", Decimal("100")),
            ("1000", "5", "0", Decimal("0")),
            ("0", "5", "2", Decimal("0")),
            ("100", "0", "5", Decimal("0")),
            ("500", "10", "3", Decimal("150")),
            ("2000", "7.5", "4", Decimal("600")),
            ("1000", "5", "0.5", Decimal("25")),
            ("1234.56", "3.25", "2", Decimal("80.2464")),
        ]
        for p, r, t, expected in table:
            with self.subTest(principal=p, rate=r, years=t):
                actual = calculate_simple_interest(p, r, t)
                self.assertEqual(actual, expected)
                self.assertIsInstance(actual, Decimal)

    def test_reference_fraction_comparison(self) -> None:
        """Verify exact agreement with independent fractions.Fraction arithmetic."""
        cases = [
            ("1000", "5", "2"),
            ("500", "10", "3"),
            ("2000", "7.5", "4"),
            ("1000", "5", "0.5"),
            ("1234.56", "3.25", "2"),
            ("9876.543", "4.125", "3.5"),
            ("0.05", "1.5", "0.25"),
        ]
        for p, r, t in cases:
            with self.subTest(principal=p, rate=r, years=t):
                actual_dec = calculate_simple_interest(p, r, t)
                expected_frac = reference_fraction_interest(p, r, t)
                self.assertEqual(Fraction(str(actual_dec)), expected_frac)

    def test_reference_annual_loop_comparison(self) -> None:
        """Verify agreement with independent iterative whole-years loop."""
        cases = [
            ("1000", "5", 1),
            ("1000", "5", 2),
            ("500", "10", 3),
            ("2000", "7.5", 4),
            ("1234.56", "3.25", 5),
        ]
        for p, r, n in cases:
            with self.subTest(principal=p, rate=r, years=n):
                actual_dec = calculate_simple_interest(p, r, n)
                loop_dec = reference_annual_loop_interest(p, r, n)
                self.assertEqual(actual_dec, loop_dec)

    def test_result_type_is_decimal_not_float(self) -> None:
        """Ensure return value is strictly a Decimal instance."""
        result = calculate_simple_interest(100, 5, 1)
        self.assertIsInstance(result, Decimal)
        self.assertNotIsInstance(result, float)

    def test_float_precision_preserved(self) -> None:
        """Floats are converted via Decimal(str(x)) so 0.1 stays 0.1."""
        result = calculate_simple_interest(100, 0.1, 1)
        self.assertEqual(result, Decimal("0.1"))

    def test_rejection_of_boolean_inputs(self) -> None:
        """Booleans must be rejected with TypeError."""
        with self.assertRaises(TypeError):
            to_decimal(True)
        with self.assertRaises(TypeError):
            to_decimal(False)
        with self.assertRaises(TypeError):
            calculate_simple_interest(True, 5, 2)
        with self.assertRaises(TypeError):
            calculate_simple_interest(1000, False, 2)
        with self.assertRaises(TypeError):
            calculate_simple_interest(1000, 5, True)

    def test_rejection_of_unsupported_types(self) -> None:
        """Unsupported types must be rejected with TypeError."""
        for val in [None, [1000], {"rate": 5}, (2,)]:
            with self.assertRaises(TypeError):
                to_decimal(val)

    def test_rejection_of_invalid_strings(self) -> None:
        """Non-numeric or empty strings must be rejected with ValueError."""
        for s in ["", "   ", "abc", "12a", "$100", "5%"]:
            with self.assertRaises(ValueError):
                to_decimal(s)

    def test_rejection_of_nan_and_infinity(self) -> None:
        """NaN and Infinity must be rejected with ValueError."""
        for non_finite in [
            Decimal("NaN"),
            float("nan"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            float("inf"),
            float("-inf"),
        ]:
            with self.assertRaises(ValueError):
                to_decimal(non_finite)

    def test_format_currency(self) -> None:
        """format_currency returns exact fixed-point string without scientific notation."""
        self.assertEqual(format_currency(Decimal("100")), "100")
        self.assertEqual(format_currency(Decimal("80.2464")), "80.2464")
        self.assertEqual(format_currency(Decimal("1e6")), "1000000")
        with self.assertRaises(TypeError):
            format_currency(100)  # type: ignore[arg-type]

    def test_clean_import(self) -> None:
        """Importing main.py via spec_from_file_location emits zero stdout/stderr."""
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        test_spec = importlib.util.spec_from_file_location(
            "clean_import_test", MAIN_PATH
        )
        self.assertIsNotNone(test_spec)
        self.assertIsNotNone(test_spec.loader)
        test_mod = importlib.util.module_from_spec(test_spec)
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            test_spec.loader.exec_module(test_mod)
        self.assertEqual(out_buf.getvalue(), "")
        self.assertEqual(err_buf.getvalue(), "")

    def test_clean_import_subprocess(self) -> None:
        """Clean import in an isolated python subprocess produces zero output."""
        code = (
            "import importlib.util, sys; "
            f"spec = importlib.util.spec_from_file_location('main_mod', r'{MAIN_PATH}'); "
            "mod = importlib.util.module_from_spec(spec); "
            "spec.loader.exec_module(mod)"
        )
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, "")
        self.assertEqual(res.stderr, "")

    def test_cli_standard_arguments(self) -> None:
        """CLI: python3 main.py 1000 5 2 prints 100 with no 'E+' and exits 0."""
        cmd = [sys.executable, str(MAIN_PATH), "1000", "5", "2"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("100", res.stdout)
        self.assertNotIn("E+", res.stdout)
        self.assertNotIn("e+", res.stdout)

    def test_cli_negative_principal_exits_nonzero(self) -> None:
        """CLI: python3 main.py -100 5 2 exits non-zero."""
        cmd = [sys.executable, str(MAIN_PATH), "-100", "5", "2"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)

    def test_cli_invalid_argument_exits_nonzero(self) -> None:
        """CLI: non-numeric argument exits non-zero."""
        cmd = [sys.executable, str(MAIN_PATH), "1000", "abc", "2"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)

    def test_cli_wrong_argument_count_exits_nonzero(self) -> None:
        """CLI: wrong number of arguments exits non-zero."""
        cmd = [sys.executable, str(MAIN_PATH), "1000", "5"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)


if __name__ == "__main__":
    unittest.main()
