"""
Unit tests for Password Strength Meter.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import random
import string
import subprocess
import sys
import unittest

MODULE_PATH = Path(__file__).resolve().parent / "main.py"
spec = importlib.util.spec_from_file_location("password_strength_meter_main", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {MODULE_PATH}")
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

check_password = main_mod.check_password
count_satisfied = main_mod.count_satisfied
format_report = main_mod.format_report
main = main_mod.main
DISCLAIMER = main_mod.DISCLAIMER


class TestPasswordStrengthMeter(unittest.TestCase):
    """Test suite covering contract, invariants, table cases, and CLI."""

    HAND_WRITTEN_TABLE: list[tuple[str, dict[str, bool], int]] = [
        ("", {"length": False, "mixed_case": False, "digit": False, "symbol": False}, 0),
        ("abc", {"length": False, "mixed_case": False, "digit": False, "symbol": False}, 0),
        ("Abc", {"length": False, "mixed_case": True, "digit": False, "symbol": False}, 1),
        ("abc123", {"length": False, "mixed_case": False, "digit": True, "symbol": False}, 1),
        ("Abc123!", {"length": False, "mixed_case": True, "digit": True, "symbol": True}, 3),
        ("Abcdefghij1!", {"length": True, "mixed_case": True, "digit": True, "symbol": True}, 4),
        ("abcdefghijkl", {"length": True, "mixed_case": False, "digit": False, "symbol": False}, 1),
        ("ABCDEFGHIJKL", {"length": True, "mixed_case": False, "digit": False, "symbol": False}, 1),
        ("!@#$%^&*()_+", {"length": True, "mixed_case": False, "digit": False, "symbol": True}, 2),
        ("123456789012", {"length": True, "mixed_case": False, "digit": True, "symbol": False}, 2),
        ("Abcdefghijkl", {"length": True, "mixed_case": True, "digit": False, "symbol": False}, 2),
        ("Abcdefghijk1", {"length": True, "mixed_case": True, "digit": True, "symbol": False}, 3),
        ("hello world!!", {"length": True, "mixed_case": False, "digit": False, "symbol": True}, 2),
        ("Zq7@kmvx", {"length": False, "mixed_case": True, "digit": True, "symbol": True}, 3),
    ]

    def test_hand_written_table(self):
        """Verify each hand-written table case matches expected condition values and count."""
        for pwd, expected_conditions, expected_count in self.HAND_WRITTEN_TABLE:
            with self.subTest(password=pwd):
                actual_conditions = check_password(pwd)
                self.assertEqual(actual_conditions, expected_conditions)
                self.assertEqual(count_satisfied(actual_conditions), expected_count)

    def test_invariant_a_satisfied_count(self):
        """Invariant A: satisfied count == number of True conditions, 0 <= count <= 4."""
        test_inputs = [pwd for pwd, _, _ in self.HAND_WRITTEN_TABLE] + [
            "short",
            "MixedCaseNoDigitOrSymbol",
            "12345",
            "!@#$",
            "OnlyLower1234567890",
            "OnlyUpper1234567890",
            "ValidWithSpacesAndTabs \t",
        ]
        for pwd in test_inputs:
            with self.subTest(password=pwd):
                res = check_password(pwd)
                cnt = count_satisfied(res)
                expected_cnt = sum(1 for v in res.values() if v)
                self.assertEqual(cnt, expected_cnt)
                self.assertGreaterEqual(cnt, 0)
                self.assertLessEqual(cnt, 4)

    def test_invariant_b_empty_string(self):
        """Invariant B: empty string -> every condition False, count 0."""
        res = check_password("")
        self.assertEqual(
            res,
            {"length": False, "mixed_case": False, "digit": False, "symbol": False},
        )
        self.assertEqual(count_satisfied(res), 0)

    def test_invariant_c_monotonicity(self):
        """Invariant C: appending any char never turns a satisfied condition False."""
        rng = random.Random(42)
        candidate_chars = string.ascii_letters + string.digits + string.punctuation + " \t\n\r" + "²éÉñ"
        base_cases = [
            "",
            "a",
            "A",
            "1",
            "!",
            "abcdefghijk",   # length 11
            "abcdefghijkl",  # length 12
            "Abcdefghijk",   # length 11 mixed
            "Abcdefghij1",   # length 11 mixed + digit
            "Abcdefghij!",   # length 11 mixed + symbol
        ]

        # Deterministic pseudo-random generation of base strings
        for _ in range(50):
            length = rng.randint(0, 20)
            base_cases.append("".join(rng.choice(candidate_chars) for _ in range(length)))

        for base in base_cases:
            base_res = check_password(base)
            base_cnt = count_satisfied(base_res)
            for _ in range(10):
                extra = rng.choice(candidate_chars)
                new_pwd = base + extra
                new_res = check_password(new_pwd)
                new_cnt = count_satisfied(new_res)

                # For every condition that was True, it must still be True
                for cond_name, satisfied in base_res.items():
                    if satisfied:
                        self.assertTrue(
                            new_res[cond_name],
                            f"Condition {cond_name} changed from True to False when appending "
                            f"{extra!r} to {base!r}",
                        )
                self.assertGreaterEqual(new_cnt, base_cnt)

    def test_invariant_d_order_independence(self):
        """Invariant D: shuffling characters does not change the result."""
        rng = random.Random(1337)
        sample_passwords = [pwd for pwd, _, _ in self.HAND_WRITTEN_TABLE if len(pwd) > 1]
        for pwd in sample_passwords:
            original_res = check_password(pwd)
            original_cnt = count_satisfied(original_res)
            for _ in range(5):
                chars = list(pwd)
                rng.shuffle(chars)
                shuffled_pwd = "".join(chars)
                shuffled_res = check_password(shuffled_pwd)
                shuffled_cnt = count_satisfied(shuffled_res)
                self.assertEqual(shuffled_res, original_res)
                self.assertEqual(shuffled_cnt, original_cnt)

    def test_invariant_e_length_boundary(self):
        """Invariant E: lengths 0, 1, 11 fail length check; 12 and 13 pass."""
        fail_lengths = [0, 1, 11]
        pass_lengths = [12, 13]

        for n in fail_lengths:
            pwd = "a" * n
            res = check_password(pwd)
            self.assertFalse(res["length"], f"Length {n} should fail length check")

        for n in pass_lengths:
            pwd = "a" * n
            res = check_password(pwd)
            self.assertTrue(res["length"], f"Length {n} should pass length check")

    def test_type_error_for_non_string(self):
        """Non-string input raises TypeError."""
        invalid_inputs = [None, 12345, 12.34, ["password"], {"pwd": "abc"}, False, b"bytes_pwd"]
        for bad_val in invalid_inputs:
            with self.subTest(val=bad_val):
                with self.assertRaises(TypeError):
                    check_password(bad_val)

    def test_digit_definition_choice_isdecimal(self):
        """Verify str.isdecimal definition: standard digits pass; superscripts do not."""
        # Standard decimal digit
        res_standard = check_password("abcdefghijk2")
        self.assertTrue(res_standard["digit"])

        # Superscript 2 is isdigit() but NOT isdecimal()
        self.assertTrue("²".isdigit())
        self.assertFalse("²".isdecimal())
        res_superscript = check_password("abcdefghijkl²")
        self.assertFalse(res_superscript["digit"])

    def test_symbol_definition_and_whitespace(self):
        """Verify symbol definition strictly matches string.punctuation; whitespace is not symbol."""
        # Whitespace does not count as symbol
        res_ws = check_password("            ")  # 12 spaces
        self.assertTrue(res_ws["length"])
        self.assertFalse(res_ws["mixed_case"])
        self.assertFalse(res_ws["digit"])
        self.assertFalse(res_ws["symbol"])
        self.assertEqual(count_satisfied(res_ws), 1)

        # Characters in string.punctuation count as symbol
        for punct in string.punctuation:
            res_punct = check_password("a" * 11 + punct)
            self.assertTrue(res_punct["symbol"], f"Punctuation char {punct!r} should satisfy symbol check")

    def test_report_text_contains_disclaimer_and_no_ratings(self):
        """format_report contains disclaimer and excludes weak/medium/strong labels."""
        report = format_report(check_password("Abcdefghij1!"))
        self.assertIn("NOT a calibrated security-strength estimate", report)
        self.assertIn("Criteria Satisfied: 4/4", report)

        # Confirm no calibrated rating labels exist in output
        lower_report = report.lower()
        for forbidden in ["weak", "medium", "strong"]:
            self.assertNotIn(forbidden, lower_report)

    def test_clean_import(self):
        """Importing main module via subprocess produces zero stdout/stderr."""
        code = (
            "import importlib.util\n"
            f"spec = importlib.util.spec_from_file_location('p_main', r'{MODULE_PATH}')\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_cli_subprocess_valid_argument(self):
        """CLI with one valid argument exits 0 and prints disclaimer."""
        proc = subprocess.run(
            [sys.executable, str(MODULE_PATH), "Abcdefghij1!"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Criteria Satisfied: 4/4", proc.stdout)
        self.assertIn("NOT a calibrated security-strength estimate", proc.stdout)
        self.assertEqual(proc.stderr, "")

    def test_cli_subprocess_wrong_argument_count(self):
        """CLI with invalid argument count exits non-zero."""
        proc = subprocess.run(
            [sys.executable, str(MODULE_PATH), "arg1", "arg2"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Error: Expected at most one password argument", proc.stderr)


if __name__ == "__main__":
    unittest.main()
