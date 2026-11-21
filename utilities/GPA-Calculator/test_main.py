"""
Unit tests for utilities/GPA-Calculator/main.py

Test discovery command:
    python3 -m unittest discover -s utilities/GPA-Calculator -p "test_*.py"

Focus areas (Task R26-T033):
- Calculate credit-weighted GPA from a supplied grade-point mapping.
- Stated contract: A=4 for 3 credits and B=3 for 1 credit gives 3.75.
- Rejection of zero total credits and unknown grades.
- Independent reference method comparison and mismatch assertion.
- Main-guarded execution: importing module does not prompt, write files, or invoke CLI.
"""

import importlib.util
import io
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent / "main.py"


def load_gpa_module():
    spec = importlib.util.spec_from_file_location("gpa_calc", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gpa_calc"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestGPACalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gpa_mod = load_gpa_module()

    def test_stated_contract_example(self):
        """
        Contract requirement:
        A=4 for 3 credits and B=3 for 1 credit gives 3.75.
        Calculation: (4*3 + 3*1) / (3 + 1) = 15 / 4 = 3.75
        """
        courses = [("A", 3), ("B", 1)]
        expected_gpa = 3.75
        actual_gpa = self.gpa_mod.calculate_gpa(courses)
        self.assertAlmostEqual(actual_gpa, expected_gpa, places=2)

    def test_zero_total_credits_rejected(self):
        """
        Zero total credits must be rejected with ValueError.
        """
        # Case A: Explicit 0 credits on a course
        with self.assertRaises(ValueError) as ctx:
            self.gpa_mod.calculate_gpa([("A", 0)])
        self.assertIn("Total credits must be greater than zero", str(ctx.exception))

        # Case B: Empty course list
        with self.assertRaises(ValueError) as ctx:
            self.gpa_mod.calculate_gpa([])
        self.assertIn("Total credits must be greater than zero", str(ctx.exception))

    def test_unknown_grades_rejected(self):
        """
        Unknown grades not present in scale must be rejected with ValueError.
        """
        with self.assertRaises(ValueError) as ctx:
            self.gpa_mod.calculate_gpa([("A", 3), ("Z_UNKNOWN", 2)])
        self.assertIn("Unknown grade", str(ctx.exception))

    def test_negative_credits_rejected(self):
        """
        Negative credits must be rejected with ValueError.
        """
        with self.assertRaises(ValueError) as ctx:
            self.gpa_mod.calculate_gpa([("A", -3)])
        self.assertIn("credits cannot be negative", str(ctx.exception))

    def test_custom_grade_scale_mapping(self):
        """
        Allows supplied custom grade scale mapping.
        """
        custom_scale = {"HONORS": 5.0, "PASS": 3.0, "FAIL": 0.0}
        courses = [("HONORS", 4), ("PASS", 2)]
        # (5.0*4 + 3.0*2) / (4 + 2) = 26 / 6 = 4.3333
        expected = round(26.0 / 6.0, 4)
        actual = self.gpa_mod.calculate_gpa(courses, grade_scale=custom_scale)
        self.assertAlmostEqual(actual, expected, places=4)

    def test_dictionary_course_input_format(self):
        """
        Supports dictionary input format: [{'grade': 'A', 'credits': 3}, ...]
        """
        courses = [{"grade": "A", "credits": 3}, {"grade": "B", "credits": 1}]
        expected = 3.75
        actual = self.gpa_mod.calculate_gpa(courses)
        self.assertEqual(actual, expected)

    def test_independent_reference_comparison(self):
        """
        Focus: Compare the result with a second simple method or an independently calculated table.
        """
        test_scenarios = [
            [("A", 3), ("B", 1)],
            [("A+", 4), ("A-", 3), ("B+", 3), ("C", 2)],
            [("A", 1.5), ("B", 2.5), ("C+", 3.0)],
        ]
        for scenario in test_scenarios:
            primary = self.gpa_mod.calculate_gpa(scenario)
            reference = self.gpa_mod.calculate_gpa_reference(scenario)
            self.assertAlmostEqual(primary, reference, places=4)

            # verify_gpa_with_reference returns matching confirmation
            result = self.gpa_mod.verify_gpa_with_reference(scenario)
            self.assertTrue(result["matched"])
            self.assertEqual(result["gpa"], primary)
            self.assertEqual(result["reference_gpa"], reference)

    def test_reference_assertion_fails_on_incorrect_result(self):
        """
        Verify that reference comparison detects and raises AssertionError
        if an incorrect result is encountered.
        """
        courses = [("A", 3), ("B", 1)]
        # Monkeypatch calculate_gpa to simulate an incorrect implementation
        original_calc = self.gpa_mod.calculate_gpa
        try:
            self.gpa_mod.calculate_gpa = lambda c, s=None: 2.50  # Incorrect return
            with self.assertRaises(AssertionError) as ctx:
                self.gpa_mod.verify_gpa_with_reference(courses)
            self.assertIn("Reference comparison mismatch", str(ctx.exception))
        finally:
            self.gpa_mod.calculate_gpa = original_calc

    def test_import_has_no_side_effects(self):
        """
        Done when: Importing the module does not prompt, write files or run the CLI.
        """
        captured_out = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_out
        try:
            # Re-import module fresh
            load_gpa_module()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(captured_out.getvalue(), "", "Importing module produced unexpected stdout output")


if __name__ == "__main__":
    unittest.main()
