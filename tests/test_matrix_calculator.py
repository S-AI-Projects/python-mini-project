"""Boundary tests for add_matrices in math/Matrix-Calculator/Matrix-Calculator.py.

Boundary Table:
| Category             | Case Description                      | Source Reference                       | Input m1                             | Input m2                             | Expected Value / Status                                                                        |
|----------------------|---------------------------------------|----------------------------------------|--------------------------------------|--------------------------------------|------------------------------------------------------------------------------------------------|
| Valid Interior       | Square 2x2                            | Line 12 ("same dimensions"), Line 15   | [[1.0, 2.0], [3.0, 4.0]]             | [[5.0, 6.0], [7.0, 8.0]]             | [[6.0, 8.0], [10.0, 12.0]]                                                                    |
| Valid Interior       | Rectangular non-square 2x3            | Line 12, Lines 13-15                   | [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]   | [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]] | [[8.0, 10.0, 12.0], [14.0, 16.0, 18.0]]                                                        |
| Valid Interior       | Floats and negative values            | Line 11 (float), Line 15               | [[-1.5, 2.5], [3.0, -4.5]]            | [[1.5, -2.5], [-3.0, 4.5]]            | [[0.0, 0.0], [0.0, 0.0]]                                                                      |
| Valid Boundary       | Minimal 1x1 matrix                    | Line 12, Lines 13-14, Lines 164-165    | [[5.0]]                              | [[3.0]]                              | [[8.0]]                                                                                        |
| Valid Boundary       | Single row vector 1x3                 | Line 12, Lines 13-15 (rows=1, cols=3)  | [[1.0, 2.0, 3.0]]                    | [[4.0, 5.0, 6.0]]                    | [[5.0, 7.0, 9.0]]                                                                              |
| Valid Boundary       | Single column vector 3x1              | Line 12, Lines 13-15 (rows=3, cols=1)  | [[1.0], [2.0], [3.0]]                | [[4.0], [5.0], [6.0]]                | [[5.0], [7.0], [9.0]]                                                                          |
| Valid Boundary       | Zero-containing matrix (all zeros)    | Line 15 (0.0 + x = x)                  | [[0.0, 0.0], [0.0, 0.0]]             | [[1.0, 2.0], [3.0, 4.0]]             | [[1.0, 2.0], [3.0, 4.0]]                                                                      |
| Valid Boundary       | Zero-containing matrix (mixed zeros)  | Line 15                                | [[0.0, 1.0], [2.0, 0.0]]             | [[3.0, 0.0], [0.0, 4.0]]             | [[3.0, 1.0], [2.0, 4.0]]                                                                      |
| Contract Invariant   | Argument Immutability Check           | Line 15 (creates new list objects)     | [[1.0, 2.0], [3.0, 4.0]]             | [[5.0, 6.0], [7.0, 8.0]]             | m1 and m2 unaltered after call                                                                 |
| Unsupported Boundary | Mismatched dimensions (fewer rows m2) | Line 12 ("same dimensions"), Line 15   | [[1.0, 2.0], [3.0, 4.0]]             | [[5.0, 6.0]]                         | Raises Exception (observed behaviour, not a specified type; does not return valid sum)         |
| Outside Domain       | Mismatched dimensions (longer m2)     | Line 12, Line 13 (rows = len(m1))      | [[1.0, 2.0], [3.0, 4.0]]             | [[5.0, 6.0], [7.0, 8.0], [9.0, 10.0]] | Undefined by source, not asserted (silently ignores extra rows)                                |
| Outside Domain       | Empty matrix input                    | Line 12, Line 14 (cols = len(m1[0]))   | []                                   | []                                   | Undefined by source, not asserted                                                              |
"""

import copy
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import patch

# Dynamically load Matrix-Calculator.py to handle hyphen in file name
_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Matrix-Calculator"
    / "Matrix-Calculator.py"
)
_SPEC = importlib.util.spec_from_file_location("matrix_calculator", _SCRIPT_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

add_matrices = _MODULE.add_matrices


class TestMatrixCalculatorAdd(unittest.TestCase):
    """Test suite defining supported boundaries of add_matrices."""

    def test_add_matrices_square_interior(self):
        """Valid interior: square 2x2 matrix addition."""
        m1 = [[1.0, 2.0], [3.0, 4.0]]
        m2 = [[5.0, 6.0], [7.0, 8.0]]
        expected = [[6.0, 8.0], [10.0, 12.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_rectangular_interior(self):
        """Valid interior: rectangular non-square 2x3 matrix addition."""
        m1 = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        m2 = [[7.0, 8.0, 9.0], [10.0, 11.0, 12.0]]
        expected = [[8.0, 10.0, 12.0], [14.0, 16.0, 18.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_float_and_negative_interior(self):
        """Valid interior: floating point and negative numbers."""
        m1 = [[-1.5, 2.5], [3.0, -4.5]]
        m2 = [[1.5, -2.5], [-3.0, 4.5]]
        expected = [[0.0, 0.0], [0.0, 0.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_single_element_boundary(self):
        """Valid boundary: minimal 1x1 matrix addition."""
        m1 = [[5.0]]
        m2 = [[3.0]]
        expected = [[8.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_row_vector_boundary(self):
        """Valid boundary: single row vector (1x3)."""
        m1 = [[1.0, 2.0, 3.0]]
        m2 = [[4.0, 5.0, 6.0]]
        expected = [[5.0, 7.0, 9.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_column_vector_boundary(self):
        """Valid boundary: single column vector (3x1)."""
        m1 = [[1.0], [2.0], [3.0]]
        m2 = [[4.0], [5.0], [6.0]]
        expected = [[5.0], [7.0], [9.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_zero_matrix_boundary(self):
        """Valid boundary: all-zero matrix acting as additive identity."""
        m1 = [[0.0, 0.0], [0.0, 0.0]]
        m2 = [[1.0, 2.0], [3.0, 4.0]]
        expected = [[1.0, 2.0], [3.0, 4.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_mixed_zeros_boundary(self):
        """Valid boundary: matrix with mixed zeros."""
        m1 = [[0.0, 1.0], [2.0, 0.0]]
        m2 = [[3.0, 0.0], [0.0, 4.0]]
        expected = [[3.0, 1.0], [2.0, 4.0]]
        self.assertEqual(add_matrices(m1, m2), expected)

    def test_add_matrices_does_not_mutate_arguments(self):
        """Contract invariant: arguments m1 and m2 are not mutated."""
        m1 = [[1.0, 2.0], [3.0, 4.0]]
        m2 = [[5.0, 6.0], [7.0, 8.0]]
        m1_copy = copy.deepcopy(m1)
        m2_copy = copy.deepcopy(m2)

        _ = add_matrices(m1, m2)

        self.assertEqual(m1, m1_copy)
        self.assertEqual(m2, m2_copy)

    def test_add_matrices_mismatched_dimensions_fewer_rows(self):
        """Unsupported boundary: m2 has fewer rows than m1 (outside 'same dimensions' contract)."""
        m1 = [[1.0, 2.0], [3.0, 4.0]]
        m2 = [[5.0, 6.0]]
        # Observed behaviour: source raises an exception on indexing when m2 has fewer rows than m1;
        # this is observed behaviour, not a specified exception type.
        with self.assertRaises(Exception):  # noqa: B017
            add_matrices(m1, m2)

    def test_module_imports_silently(self):
        """Verify that importing the module produces zero stdout/stderr and requires no stdin."""
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        with patch("sys.stdout", stdout_buf), patch("sys.stderr", stderr_buf):
            spec = importlib.util.spec_from_file_location("matrix_calc_silent", _SCRIPT_PATH)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        self.assertEqual(stdout_buf.getvalue(), "")
        self.assertEqual(stderr_buf.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
