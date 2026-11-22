"""
Complexity scaling and correctness regression tests for `print_puzzle` in games/Spot-the-Difference/Spot-the-Difference.py.

Task ID: R26-T059
Preconditions & Fixture Anchors:
- PUZZLES definition  (Spot-the-Difference.py, lines 15-43)
- print_puzzle        (Spot-the-Difference.py, line 46)
- row loop            (Spot-the-Difference.py, line 52)
- ruler generator     (Spot-the-Difference.py, line 55)
"""

import importlib.util
import io
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Spot-the-Difference"
    / "Spot-the-Difference.py"
)


def load_module():
    """Load Spot-the-Difference module safely."""
    spec = importlib.util.spec_from_file_location("spot_the_difference", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSpotTheDifferenceScaling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_smallest_valid_input_single_character(self):
        """Case 1: Smallest valid input domain boundary (1x1 puzzle).

        Preconditions:
        - Line 46: def print_puzzle(puzzle)
        - Line 52: for row_number, (left, right) in enumerate(...)
        - Line 55: column ruler for width 1
        Literal input: left=["A"], right=["B"]
        """
        puzzle = {
            "left": ["A"],
            "right": ["B"],
            "answer": (1, 1),
        }

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            self.module.print_puzzle(puzzle)

        output = captured.getvalue()

        # Independently calculated expected lines
        self.assertIn("Find the one changed character in the right image.", output)
        self.assertIn("1. A      B", output)
        self.assertIn("   1", output)

    def test_ordinary_valid_input_builtin_puzzle(self):
        """Case 2: Ordinary input from built-in PUZZLES fixture (3x11).

        Preconditions:
        - Lines 36-42: PUZZLES[2] definition
        """
        puzzle = {
            "left": [
                "  *     *  ",
                "    *      ",
                " *    *    ",
            ],
            "right": [
                "  *     *  ",
                "    *      ",
                " *    **   ",
            ],
            "answer": (3, 7),
        }

        captured = io.StringIO()
        with patch("sys.stdout", captured):
            self.module.print_puzzle(puzzle)

        output = captured.getvalue()

        self.assertIn("1.   *     *          *     *  ", output)
        self.assertIn("2.     *                *      ", output)
        self.assertIn("3.  *    *           *    **   ", output)
        # Expected column ruler for width 11: 12345678901
        self.assertIn("   12345678901", output)

    def test_complexity_scaling_experiment(self):
        """Case 3: Measure empirical scaling over 3 increasing input sizes with 5 repetitions.

        Validates that correctness is maintained across all sizes and collects
        scaling metrics without making test pass/fail conditional on wall-clock jitter.
        """
        sizes = [
            ("Small", 3, 11),
            ("Medium", 10, 25),
            ("Large", 50, 100),
        ]

        metrics = {}

        for label, r, c in sizes:
            durations = []
            test_puzzle = {
                "left": ["." * c for _ in range(r)],
                "right": ["." * c for _ in range(r)],
                "answer": (1, 1),
            }

            for rep in range(5):
                captured = io.StringIO()
                t0 = time.perf_counter()
                with patch("sys.stdout", captured):
                    self.module.print_puzzle(test_puzzle)
                t1 = time.perf_counter()

                output = captured.getvalue()
                # Correctness assertions outside timed region
                self.assertIn(f"{r}. " + "." * c, output)
                self.assertIn("   " + "".join(str((i % 10) or 0) for i in range(1, c + 1)), output)

                durations.append(t1 - t0)

            durations.sort()
            median_time = durations[len(durations) // 2]
            time_range = durations[-1] - durations[0]
            metrics[label] = {
                "rows": r,
                "cols": c,
                "median_sec": median_time,
                "range_sec": time_range,
                "total_chars": r * c,
            }

        # Verify monotonicity of problem scale
        self.assertLess(metrics["Small"]["total_chars"], metrics["Medium"]["total_chars"])
        self.assertLess(metrics["Medium"]["total_chars"], metrics["Large"]["total_chars"])
