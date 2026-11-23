"""
Regression tests for math/Collatz-Conjecture/Collatz-Conjecture.py (Task R26-T041).

Locks down the contract of collatz_next:
- Smallest valid input: n = 1 -> expected 4
- Ordinary even input: n = 4 -> expected 2, n = 6 -> expected 3
- Ordinary odd input: n = 3 -> expected 10, n = 5 -> expected 16
- Domain boundary / cycle value: n = 2 -> expected 1
- Preserves global state without mutation: steps_cache = {1: 0} (line 6), seq = [] (line 14)
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "math" / "Collatz-Conjecture" / "Collatz-Conjecture.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("collatz_conjecture", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["collatz_conjecture"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestCollatzContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_smallest_valid_input(self):
        # Smallest valid positive integer (n = 1) -> 3*1 + 1 = 4
        # Source line anchor: steps_cache = {1: 0} at line 6
        expected = 4
        actual = self.mod.collatz_next(1)
        self.assertEqual(actual, expected)

    def test_ordinary_inputs(self):
        # Ordinary odd input: 3 -> 3*3 + 1 = 10
        self.assertEqual(self.mod.collatz_next(3), 10)
        # Ordinary even input: 6 -> 6 // 2 = 3
        self.assertEqual(self.mod.collatz_next(6), 3)
        # Another ordinary odd input: 5 -> 3*5 + 1 = 16
        self.assertEqual(self.mod.collatz_next(5), 16)
        # Another ordinary even input: 4 -> 4 // 2 = 2
        self.assertEqual(self.mod.collatz_next(4), 2)

    def test_domain_boundary_repeated_cycle(self):
        # 2 -> 1 (transition to terminal state 1)
        self.assertEqual(self.mod.collatz_next(2), 1)

    def test_no_observable_mutation(self):
        # Verify steps_cache at line 6 is not mutated by calling collatz_next
        cache_before = dict(self.mod.steps_cache)
        self.assertEqual(cache_before, {1: 0})
        _ = self.mod.collatz_next(7)
        self.assertEqual(self.mod.steps_cache, {1: 0})


if __name__ == "__main__":
    unittest.main()
