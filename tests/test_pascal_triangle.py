"""
Failure behavior and domain boundary regression tests for `generate_pascal_triangle` in math/Pascal-Triangle/Pascal-Triangle.py.

Task ID: R26-T058
Preconditions & Fixture Anchors:
- if n <= 0: return []    (Pascal-Triangle.py, lines 12-13 / 27-28)
- triangle = []           (Pascal-Triangle.py, line 14 / 29)
- row = [1]               (Pascal-Triangle.py, line 17 / 32)
"""

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Pascal-Triangle"
    / "Pascal-Triangle.py"
)


def load_module():
    """Load Pascal-Triangle module safely."""
    spec = importlib.util.spec_from_file_location("pascal_triangle", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPascalTriangleFailureContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_absent_result_failure_boundary_zero(self):
        """Case 1: Absent-result failure branch for boundary input n = 0.

        Preconditions:
        - Line 12-13: `if n <= 0: return []`
        - Line 14: triangle = [] (empty fixture anchor)
        - Line 17: row = [1]
        Literal input: n = 0
        """
        caller_state = {"history": ["initial"]}

        # Act: trigger absent-result failure path
        result = self.module.generate_pascal_triangle(0)

        # Assert returned value is empty list sentinel
        expected_result = []
        self.assertEqual(
            result,
            expected_result,
            f"Expected {expected_result} for n=0, got {result}",
        )

        # Assert caller state remains completely valid
        self.assertEqual(caller_state, {"history": ["initial"]})

    def test_absent_result_failure_branch_negative(self):
        """Case 2: Absent-result failure branch for out-of-domain negative input n = -5.

        Preconditions:
        - Line 12-13: `if n <= 0: return []`
        Literal input: n = -5
        """
        result = self.module.generate_pascal_triangle(-5)
        self.assertEqual(result, [])

    def test_smallest_valid_input_one_row(self):
        """Case 3: Smallest valid non-empty input domain (n = 1).

        Preconditions:
        - Line 14: triangle = []
        - Line 17: row = [1]
        Literal input: n = 1
        """
        result = self.module.generate_pascal_triangle(1)
        expected_result = [[1]]
        self.assertEqual(
            result,
            expected_result,
            f"Expected {expected_result} for n=1, got {result}",
        )

    def test_ordinary_valid_input_four_rows(self):
        """Case 4: Ordinary valid input domain (n = 4).

        Preconditions:
        - Line 14: triangle = []
        - Line 17: row = [1]
        - Line 20: row.append(triangle[i-1][j-1] + triangle[i-1][j])
        Literal input: n = 4
        """
        result = self.module.generate_pascal_triangle(4)
        expected_result = [
            [1],
            [1, 1],
            [1, 2, 1],
            [1, 3, 3, 1],
        ]
        self.assertEqual(
            result,
            expected_result,
            f"Expected {expected_result} for n=4, got {result}",
        )

    def test_success_after_failure_sequence(self):
        """Case 5: Verification that ordinary valid call succeeds cleanly after failure call.

        Ensures no cached corruption or internal leakage between invocations.
        """
        # First: invoke failure path
        fail_result = self.module.generate_pascal_triangle(0)
        self.assertEqual(fail_result, [])

        # Second: immediately invoke valid ordinary input
        success_result = self.module.generate_pascal_triangle(3)
        expected_success = [
            [1],
            [1, 1],
            [1, 2, 1],
        ]
        self.assertEqual(success_result, expected_success)
