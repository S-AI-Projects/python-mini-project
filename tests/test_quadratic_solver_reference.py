"""
Reference comparison regression tests for math/Quadratic-Solver/Quadratic-Solver.py (Task R26-T043).

Compares solve_quadratic against an independent reference table of 20+ inputs.
Precondition anchor: a != 0 (checked at line 24 of Quadratic-Solver.py).
Fixture inputs:
- Smallest valid input: a = 1, b = 0, c = 0 -> ('repeated_real', 0.0, 0.0, 0.0)
- Ordinary input: a = 1, b = -3, c = 2 -> ('distinct_real', 2.0, 1.0, 1.0)
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "math" / "Quadratic-Solver" / "Quadratic-Solver.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("quadratic_solver", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["quadratic_solver"] = mod
    spec.loader.exec_module(mod)
    return mod


# 20+ independently verified oracle cases: (a, b, c, expected_kind, expected_r1, expected_r2, expected_d)
REFERENCE_CASES = [
    # 1. Smallest valid input
    (1, 0, 0, "repeated_real", 0.0, 0.0, 0.0),
    # 2. Ordinary input (factored (x-2)(x-1))
    (1, -3, 2, "distinct_real", 2.0, 1.0, 1.0),
    # 3. Factored (x-3)(x-2) = x^2 - 5x + 6
    (1, -5, 6, "distinct_real", 3.0, 2.0, 1.0),
    # 4. Factored (x+1)(x-1) = x^2 - 1
    (1, 0, -1, "distinct_real", 1.0, -1.0, 4.0),
    # 5. Factored (x+2)(x+3) = x^2 + 5x + 6
    (1, 5, 6, "distinct_real", -2.0, -3.0, 1.0),
    # 6. Factored (2x-1)(x-2) = 2x^2 - 5x + 2
    (2, -5, 2, "distinct_real", 2.0, 0.5, 9.0),
    # 7. Repeated root at 1: (x-1)^2 = x^2 - 2x + 1
    (1, -2, 1, "repeated_real", 1.0, 1.0, 0.0),
    # 8. Repeated root at -1: (x+1)^2 = x^2 + 2x + 1
    (1, 2, 1, "repeated_real", -1.0, -1.0, 0.0),
    # 9. Repeated root at 2: (x-2)^2 = x^2 - 4x + 4
    (1, -4, 4, "repeated_real", 2.0, 2.0, 0.0),
    # 10. Repeated root at -2: (x+2)^2 = x^2 + 4x + 4
    (1, 4, 4, "repeated_real", -2.0, -2.0, 0.0),
    # 11. Repeated root scaled: 4x^2 - 4x + 1 = (2x-1)^2
    (4, -4, 1, "repeated_real", 0.5, 0.5, 0.0),
    # 12. Complex roots: x^2 + 1 = 0 -> +/- 1j
    (1, 0, 1, "complex", 1j, -1j, -4.0),
    # 13. Complex roots: x^2 + 4 = 0 -> +/- 2j
    (1, 0, 4, "complex", 2j, -2j, -16.0),
    # 14. Complex roots: x^2 - 2x + 2 = 0 -> 1 +/- 1j
    (1, -2, 2, "complex", 1.0 + 1j, 1.0 - 1j, -4.0),
    # 15. Complex roots: x^2 + 2x + 2 = 0 -> -1 +/- 1j
    (1, 2, 2, "complex", -1.0 + 1j, -1.0 - 1j, -4.0),
    # 16. Negative leading coefficient: -x^2 + 3x - 2 = 0 -> 1.0 and 2.0
    (-1, 3, -2, "distinct_real", 1.0, 2.0, 1.0),
    # 17. Negative leading coefficient repeated: -x^2 + 2x - 1 = 0 -> 1.0
    (-1, 2, -1, "repeated_real", 1.0, 1.0, 0.0),
    # 18. Factored (x-4)(x+2) = x^2 - 2x - 8
    (1, -2, -8, "distinct_real", 4.0, -2.0, 36.0),
    # 19. Factored (x-5)(x-1) = x^2 - 6x + 5
    (1, -6, 5, "distinct_real", 5.0, 1.0, 16.0),
    # 20. Factored (2x+3)(x-1) = 2x^2 + x - 3
    (2, 1, -3, "distinct_real", 1.0, -1.5, 25.0),
    # 21. Pure imaginary scaled: 2x^2 + 8 = 0 -> +/- 2j
    (2, 0, 8, "complex", 2j, -2j, -64.0),
]


class TestQuadraticSolverReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_precondition_a_zero_raises(self):
        # Precondition check: a == 0 raises ValueError (line 24)
        with self.assertRaises(ValueError):
            self.mod.solve_quadratic(0, 2, 1)

    def test_smallest_valid_input_fixture(self):
        # Smallest valid input: a=1, b=0, c=0
        kind, r1, r2, d = self.mod.solve_quadratic(1, 0, 0)
        self.assertEqual(kind, "repeated_real")
        self.assertEqual(r1, 0.0)
        self.assertEqual(r2, 0.0)
        self.assertEqual(d, 0.0)

    def test_ordinary_input_fixture(self):
        # Ordinary input: a=1, b=-3, c=2
        kind, r1, r2, d = self.mod.solve_quadratic(1, -3, 2)
        self.assertEqual(kind, "distinct_real")
        self.assertEqual(r1, 2.0)
        self.assertEqual(r2, 1.0)
        self.assertEqual(d, 1.0)

    def test_all_reference_cases(self):
        for a, b, c, exp_kind, exp_r1, exp_r2, exp_d in REFERENCE_CASES:
            kind, r1, r2, d = self.mod.solve_quadratic(a, b, c)
            self.assertEqual(kind, exp_kind, f"Kind mismatch for ({a},{b},{c})")
            self.assertAlmostEqual(d, exp_d, places=7, msg=f"d mismatch for ({a},{b},{c})")
            # If complex or float, check root values (allowing order invariance)
            actual_roots = sorted([r1, r2], key=lambda x: (x.real, x.imag if isinstance(x, complex) else 0))
            expected_roots = sorted([exp_r1, exp_r2], key=lambda x: (x.real, x.imag if isinstance(x, complex) else 0))
            for act, exp in zip(actual_roots, expected_roots):
                if isinstance(exp, complex):
                    self.assertAlmostEqual(act.real, exp.real, places=7)
                    self.assertAlmostEqual(act.imag, exp.imag, places=7)
                else:
                    self.assertAlmostEqual(act, exp, places=7)


if __name__ == "__main__":
    unittest.main()
