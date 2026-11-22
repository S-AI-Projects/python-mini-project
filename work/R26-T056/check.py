#!/usr/bin/env python3
"""
Focused regression test runner for R26-T056: Blackjack suits get_heart_points refactoring.

Usage:
    python3 work/R26-T056/check.py

Requirements:
- Imports or invokes only the named module / tests.
- Mocks external I/O if needed.
- Confirms before/after parity and explicit calculations.
- Returns exit code 0 on success, non-zero on failure.
"""

import sys
import os
from pathlib import Path
import unittest

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_blackjack_suits import TestGetHeartPointsRefactor


def main():
    print("=" * 70)
    print("R26-T056: Blackjack-21 - `get_heart_points` Refactoring Parity Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: games/Blackjack-21/suits.py -> get_heart_points()")
    print("Domain: Parametric cardioid evaluation, Y-sign orientation, zero cache mutation")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGetHeartPointsRefactor)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("-" * 70)
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print(f"Tests executed: {total}")
    print(f"Passed:         {passed}")
    print(f"Failed:         {failures}")
    print(f"Errors:         {errors}")
    print("=" * 70)

    if not result.wasSuccessful():
        print("\n❌ REGRESSION TESTS FAILED")
        for test, trace in result.failures + result.errors:
            print(f"\nFailure in {test}:")
            print(trace)
        sys.exit(1)
    else:
        print("\n✅ ALL REGRESSION TESTS PASSED (refactoring verified bit-identical)")
        sys.exit(0)


if __name__ == "__main__":
    main()
