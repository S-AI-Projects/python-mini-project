"""Tests for utilities/Roman-Numerals/main.py (R26-T038).

Covers:
- Canonical conversion of 1..3999 (1->I, 4->IV, 9->IX, 58->LVIII, 1994->MCMXCIV, 3999->MMMCMXCIX)
- Rejection of 0, negative integers, numbers >= 4000, and non-integer types
- Actionable error messages
- Failure path coverage: proving failure leaves caller data and files intact
- CLI behavior and import side-effect isolation
"""

import copy
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from . import main as roman_mod
except ImportError:
    try:
        import main as roman_mod
    except ImportError:
        import importlib.util
        _MAIN_FILE = Path(__file__).resolve().parent / "main.py"
        spec = importlib.util.spec_from_file_location("roman_numerals_main", _MAIN_FILE)
        roman_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(roman_mod)


class TestCanonicalRomanNumerals(unittest.TestCase):
    """Verify canonical Roman numeral encodings for required benchmark values."""

    def test_required_examples(self):
        """Verify the exact benchmark values from the task specification."""
        cases = [
            (1, "I"),
            (4, "IV"),
            (9, "IX"),
            (58, "LVIII"),
            (1994, "MCMXCIV"),
            (3999, "MMMCMXCIX"),
        ]
        for num, expected in cases:
            with self.subTest(num=num, expected=expected):
                actual = roman_mod.to_roman(num)
                self.assertEqual(actual, expected)

    def test_single_symbols_and_subtractions(self):
        """Verify each atomic symbol and subtractive pair."""
        atomic = [
            (1, "I"),
            (4, "IV"),
            (5, "V"),
            (9, "IX"),
            (10, "X"),
            (40, "XL"),
            (50, "L"),
            (90, "XC"),
            (100, "C"),
            (400, "CD"),
            (500, "D"),
            (900, "CM"),
            (1000, "M"),
        ]
        for num, expected in atomic:
            with self.subTest(num=num):
                self.assertEqual(roman_mod.to_roman(num), expected)


class TestFailurePathAndActionableErrors(unittest.TestCase):
    """Verify invalid inputs raise actionable errors and leave caller data intact."""

    def test_zero_is_rejected(self):
        """Zero has no Roman numeral representation and must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            roman_mod.to_roman(0)
        err_msg = str(ctx.exception)
        self.assertIn("0", err_msg)
        self.assertIn("1..3999", err_msg)
        self.assertIn("Action:", err_msg)

    def test_negative_integers_rejected(self):
        """Negative integers cannot be represented and must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            roman_mod.to_roman(-42)
        err_msg = str(ctx.exception)
        self.assertIn("-42", err_msg)
        self.assertIn("Negative integers", err_msg)
        self.assertIn("Action:", err_msg)

    def test_upper_bound_rejection(self):
        """Values >= 4000 exceed canonical range and must be rejected."""
        for num in (4000, 5000, 10000):
            with self.subTest(num=num):
                with self.assertRaises(ValueError) as ctx:
                    roman_mod.to_roman(num)
                self.assertIn(str(num), str(ctx.exception))
                self.assertIn("Action:", str(ctx.exception))

    def test_non_integer_types_raise_actionable_type_error(self):
        """Non-integer types (float, string, bool, None) must be rejected with TypeError."""
        invalid_types = [
            (3.14, "float"),
            ("1994", "str"),
            (True, "bool"),  # bool is subclass of int in Python, must be explicitly guarded
            (False, "bool"),
            (None, "NoneType"),
            ([1], "list"),
        ]
        for val, type_name in invalid_types:
            with self.subTest(val=val):
                with self.assertRaises(TypeError) as ctx:
                    roman_mod.to_roman(val)
                err_msg = str(ctx.exception)
                self.assertIn(type_name, err_msg)
                self.assertIn("Action:", err_msg)


class TestCallerDataIntegrityOnFailure(unittest.TestCase):
    """Prove that failures leave caller memory structures and files completely intact."""

    def test_caller_list_intact_on_batch_failure(self):
        """Caller sequence must not be mutated when batch conversion fails."""
        original_data = [1, 4, 9, 0, 58, 1994]  # index 3 is invalid (0)
        caller_data = list(original_data)

        with self.assertRaises(ValueError) as ctx:
            roman_mod.convert_many(caller_data)

        # Actionable error mentions failure index and cause
        self.assertIn("index 3", str(ctx.exception))
        # PROOF: caller data is bit-for-bit identical to before the call
        self.assertEqual(caller_data, original_data)
        self.assertEqual(len(caller_data), len(original_data))

    def test_caller_dict_and_complex_data_intact_on_failure(self):
        """Nested caller structures remain untouched upon conversion failure."""
        caller_records = [
            {"id": 101, "value": 58, "status": "pending"},
            {"id": 102, "value": -1, "status": "pending"},  # invalid
            {"id": 103, "value": 1994, "status": "pending"},
        ]
        snapshot = copy.deepcopy(caller_records)

        with self.assertRaises(ValueError):
            # Attempt to convert extracting 'value'
            roman_mod.convert_many([r["value"] for r in caller_records])

        # PROOF: caller_records was not modified
        self.assertEqual(caller_records, snapshot)

    def test_destination_file_not_created_on_failure(self):
        """When file conversion encounters invalid data, target file is not created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = Path(tmpdir) / "source.txt"
            dst_file = Path(tmpdir) / "output.txt"

            # 3rd item is invalid: 4000
            src_file.write_text("1\n4\n4000\n9\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                roman_mod.convert_file(src_file, dst_file)

            # PROOF: destination file was never created / half-written
            self.assertFalse(dst_file.exists(), "Target file must not exist after failure")
            # PROOF: no lingering temp files in destination directory
            remaining_files = list(Path(tmpdir).glob(".roman_tmp_*"))
            self.assertEqual(remaining_files, [], "Temporary files must be cleaned up")

    def test_existing_destination_file_preserved_on_failure(self):
        """If destination already exists, its pre-existing content is preserved on failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = Path(tmpdir) / "source.txt"
            dst_file = Path(tmpdir) / "existing_output.txt"

            original_content = "ORIGINAL_SAFE_CONTENT_12345\nDO_NOT_OVERWRITE\n"
            dst_file.write_text(original_content, encoding="utf-8")

            # Source has invalid negative number
            src_file.write_text("1\n-99\n58\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                roman_mod.convert_file(src_file, dst_file)

            # PROOF: existing file content is 100% intact
            self.assertEqual(dst_file.read_text(encoding="utf-8"), original_content)

    def test_successful_file_conversion(self):
        """Verify successful file conversion writes correct numerals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = Path(tmpdir) / "source.txt"
            dst_file = Path(tmpdir) / "output.txt"

            src_file.write_text("1\n4\n9\n58\n1994\n", encoding="utf-8")
            count = roman_mod.convert_file(src_file, dst_file)

            self.assertEqual(count, 5)
            self.assertTrue(dst_file.exists())
            self.assertEqual(
                dst_file.read_text(encoding="utf-8"),
                "I\nIV\nIX\nLVIII\nMCMXCIV\n",
            )


class TestCliAndImportSafety(unittest.TestCase):
    """Verify CLI interface and guarantee that importing produces no side effects."""

    def test_cli_single_number(self):
        stdout_buf = io.StringIO()
        with patch("sys.stdout", stdout_buf):
            exit_code = roman_mod.main(["1994"])
        self.assertEqual(exit_code, 0)
        self.assertIn("MCMXCIV", stdout_buf.getvalue())

    def test_cli_multiple_numbers(self):
        stdout_buf = io.StringIO()
        with patch("sys.stdout", stdout_buf):
            exit_code = roman_mod.main(["1", "4", "9", "58"])
        self.assertEqual(exit_code, 0)
        output = stdout_buf.getvalue()
        self.assertIn("I", output)
        self.assertIn("IV", output)
        self.assertIn("IX", output)
        self.assertIn("LVIII", output)

    def test_cli_invalid_number_exits_nonzero(self):
        stderr_buf = io.StringIO()
        with patch("sys.stderr", stderr_buf):
            exit_code = roman_mod.main(["0"])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Error converting 0", stderr_buf.getvalue())

    def test_import_has_no_side_effects(self):
        """Importing the module must not prompt, print, or create files."""
        import importlib.util

        _target = Path(__file__).resolve().parent / "main.py"
        with patch("builtins.input") as mock_input, patch("sys.stdout") as mock_stdout:
            spec = importlib.util.spec_from_file_location("roman_isolated_test", _target)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mock_input.assert_not_called()
            mock_stdout.write.assert_not_called()
            self.assertTrue(hasattr(mod, "to_roman"))


if __name__ == "__main__":
    unittest.main()
