"""
Unit tests for Matrix Determinant calculator.
"""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest

# Ensure the module directory is accessible for direct import
MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from main import (
    calculate_determinant,
    determinant,
    parse_matrix,
    validate_square_matrix,
)


class TestMatrixDeterminantContract(unittest.TestCase):
    """Regression tests for the explicit contract and dimension validation."""

    def test_contract_2x2(self):
        """Verify [[1,2],[3,4]] evaluates to -2."""
        self.assertEqual(calculate_determinant([[1, 2], [3, 4]]), -2)
        self.assertEqual(determinant([[1, 2], [3, 4]]), -2)

    def test_contract_1x1(self):
        """Verify [[5]] evaluates to 5."""
        self.assertEqual(calculate_determinant([[5]]), 5)
        self.assertEqual(determinant([[5]]), 5)

    def test_nonsquare_rejected_more_columns(self):
        """Verify 2x3 matrix [[1,2,3],[4,5,6]] raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_determinant([[1, 2, 3], [4, 5, 6]])

    def test_nonsquare_rejected_column_vector(self):
        """Verify 2x1 matrix [[1],[2]] raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_determinant([[1], [2]])

    def test_nonsquare_rejected_row_vector(self):
        """Verify 1x2 matrix [[1,2]] raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_determinant([[1, 2]])

    def test_ragged_matrix_rejected(self):
        """Verify ragged matrix [[1,2],[3]] raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_determinant([[1, 2], [3]])

    def test_empty_matrix_rejected(self):
        """Verify empty lists [] and [[]] raise ValueError."""
        with self.assertRaises(ValueError):
            calculate_determinant([])
        with self.assertRaises(ValueError):
            calculate_determinant([[]])

    def test_bool_rejected_with_type_error(self):
        """Verify boolean elements are rejected with TypeError."""
        with self.assertRaises(TypeError):
            calculate_determinant([[True, 0], [0, 1]])
        with self.assertRaises(TypeError):
            calculate_determinant([[False]])
        with self.assertRaises(TypeError):
            validate_square_matrix([[1, True], [0, 1]])

    def test_non_numeric_rejected_with_type_error(self):
        """Verify non-numeric values raise TypeError."""
        with self.assertRaises(TypeError):
            calculate_determinant([["a", 1], [2, 3]])
        with self.assertRaises(TypeError):
            calculate_determinant([[None]])
        with self.assertRaises(TypeError):
            validate_square_matrix("not a matrix")
        with self.assertRaises(TypeError):
            validate_square_matrix(["not a list row"])

    def test_3x3_matrix(self):
        """Verify 3x3 matrix determinant calculation."""
        # det([[6, 1, 1], [4, -2, 5], [2, 8, 7]]) = -306
        mat = [
            [6, 1, 1],
            [4, -2, 5],
            [2, 8, 7],
        ]
        self.assertEqual(calculate_determinant(mat), -306)

    def test_4x4_matrix(self):
        """Verify 4x4 matrix determinant calculation."""
        mat = [
            [1, 0, 2, -1],
            [3, 0, 0, 5],
            [2, 1, 4, -3],
            [1, 0, 5, 0],
        ]
        self.assertEqual(calculate_determinant(mat), 30)

    def test_identity_matrix(self):
        """Verify identity matrix of size 3 has determinant 1."""
        identity = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]
        self.assertEqual(calculate_determinant(identity), 1)

    def test_singular_matrix(self):
        """Verify singular matrix (linearly dependent rows) has determinant 0."""
        singular = [
            [1, 2, 3],
            [2, 4, 6],
            [7, 8, 9],
        ]
        self.assertEqual(calculate_determinant(singular), 0)

    def test_float_matrix(self):
        """Verify float matrix calculation with correct decimal handling."""
        mat = [
            [2.5, 1.5],
            [0.5, 4.0],
        ]
        # 2.5 * 4.0 - 1.5 * 0.5 = 10.0 - 0.75 = 9.25
        self.assertAlmostEqual(calculate_determinant(mat), 9.25)

    def test_clean_import_no_side_effects(self):
        """Verify that importing main produces no stdout/stderr or prompts."""
        main_path = MODULE_DIR / "main.py"
        spec = importlib.util.spec_from_file_location("main_import_test", main_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()

        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            spec.loader.exec_module(module)

        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(stderr_buf.getvalue(), "")

    def test_parse_matrix_safe(self):
        """Verify parse_matrix correctly parses string formats and rejects invalid."""
        self.assertEqual(parse_matrix("[[1, 2], [3, 4]]"), [[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            parse_matrix("")
        with self.assertRaises(ValueError):
            parse_matrix("invalid syntax {{{")

    def test_cli_subprocess_non_zero_exit_on_invalid_input(self):
        """Verify CLI exits non-zero via subprocess when given invalid matrix."""
        main_path = MODULE_DIR / "main.py"
        proc = subprocess.run(
            [sys.executable, str(main_path), "[[1,2],[3]]"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Error:", proc.stdout)

    def test_cli_subprocess_success(self):
        """Verify CLI exits zero via subprocess when given valid matrix."""
        main_path = MODULE_DIR / "main.py"
        proc = subprocess.run(
            [sys.executable, str(main_path), "[[1,2],[3,4]]"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("-2", proc.stdout)


if __name__ == "__main__":
    unittest.main()
