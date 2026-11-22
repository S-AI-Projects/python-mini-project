#!/usr/bin/env python3
"""
Focused regression test runner for R26-T055: Tower of Hanoi main function repeatability.

Usage:
    python3 work/R26-T055/check.py

Requirements:
- Controls external state (UI / Tkinter dependencies).
- Verifies repeated calls and input isolation.
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

from tests.test_tower_of_hanoi_main import TestTowerOfHanoiMainRepeatability


def main():
    print("=" * 70)
    print("R26-T055: Tower of Hanoi - `main` Repeatability & Isolation Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: utilities/Tower-of-Hanoi/Tower-of-Hanoi.py -> main()")
    print("Domain: Controlled Tkinter root injection, input isolation, repeatability")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTowerOfHanoiMainRepeatability)

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
        print("\n✅ ALL REGRESSION TESTS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
