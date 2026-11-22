"""
Focused regression tests for `get_heart_points` refactoring in games/Blackjack-21/suits.py.

Task ID: R26-T056
Preconditions & Fixture Anchors:
- SUIT_CACHE = {}  (suits.py, line 5)
- points = []      (suits.py, line 9/18)
- get_heart_points (suits.py, line 7)
"""

import importlib.util
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock

# Provide mock dependencies if pygame is not installed in the environment
if "pygame" not in sys.modules:
    sys.modules["pygame"] = MagicMock()

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Blackjack-21"
    / "suits.py"
)


def load_module():
    """Load suits module safely."""
    spec = importlib.util.spec_from_file_location("blackjack_suits", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_heart_points_reference(cx, cy, scale, invert=False):
    """Independent canonical reference implementation for verification."""
    pts = []
    for i in range(360):
        t = math.radians(i)
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        if invert:
            pts.append((cx + x * scale, cy + y * scale))
        else:
            pts.append((cx + x * scale, cy - y * scale))
    return pts


class TestGetHeartPointsRefactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_smallest_valid_input_zero_scale(self):
        """Case 1: Smallest valid input domain boundary (cx=0, cy=0, scale=0, invert=False).

        Preconditions:
        - Source line 5: SUIT_CACHE = {} (must remain unmutated)
        - Source line 9: points = [] (initial empty state)
        - Literal input: cx=0, cy=0, scale=0, invert=False
        """
        initial_cache_keys = list(self.module.SUIT_CACHE.keys())
        expected_points = [(0.0, 0.0)] * 360

        result = self.module.get_heart_points(0, 0, 0, invert=False)

        # Assert shape and exact values
        self.assertEqual(len(result), 360)
        self.assertEqual(result, expected_points)

        # Assert zero mutation on global cache
        self.assertEqual(list(self.module.SUIT_CACHE.keys()), initial_cache_keys)

    def test_ordinary_valid_input_upright_heart(self):
        """Case 2: Ordinary input for standard upright heart (cx=100, cy=100, scale=1.5, invert=False).

        Preconditions:
        - Source line 5: SUIT_CACHE = {}
        - Source line 9: points = []
        """
        cx, cy, scale, invert = 100, 100, 1.5, False
        expected_points = canonical_heart_points_reference(cx, cy, scale, invert)

        result = self.module.get_heart_points(cx, cy, scale, invert=invert)

        self.assertEqual(len(result), 360)
        for i, (actual_pt, expected_pt) in enumerate(zip(result, expected_points)):
            self.assertAlmostEqual(
                actual_pt[0],
                expected_pt[0],
                places=9,
                msg=f"Mismatch at index {i} x coordinate",
            )
            self.assertAlmostEqual(
                actual_pt[1],
                expected_pt[1],
                places=9,
                msg=f"Mismatch at index {i} y coordinate",
            )

    def test_ordinary_valid_input_inverted_spade(self):
        """Case 3: Inverted heart (spade orientation) (cx=80, cy=120, scale=2.0, invert=True).

        Preconditions:
        - Source line 5: SUIT_CACHE = {}
        """
        cx, cy, scale, invert = 80, 120, 2.0, True
        expected_points = canonical_heart_points_reference(cx, cy, scale, invert)

        result = self.module.get_heart_points(cx, cy, scale, invert=invert)

        self.assertEqual(len(result), 360)
        for i, (actual_pt, expected_pt) in enumerate(zip(result, expected_points)):
            self.assertAlmostEqual(actual_pt[0], expected_pt[0], places=9)
            self.assertAlmostEqual(actual_pt[1], expected_pt[1], places=9)

    def test_cache_isolation_and_purity(self):
        """Case 4: SUIT_CACHE remains pure and unmutated across repeated calls."""
        initial_len = len(self.module.SUIT_CACHE)
        self.module.get_heart_points(50, 50, 1.0, invert=False)
        self.module.get_heart_points(50, 50, 1.0, invert=True)
        self.assertEqual(len(self.module.SUIT_CACHE), initial_len)
