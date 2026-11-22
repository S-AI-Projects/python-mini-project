#!/usr/bin/env python3
"""
Focused regression test runner for R26-T058: Pascal Triangle generate_pascal_triangle failure behavior.

Usage:
    python3 work/R26-T058/check.py

Requirements:
- Exercises documented failure / absent-result branch (`n <= 0 -> []`).
- Confirms caller state preservation and success after failure.
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

from tests.test_pascal_triangle import TestPascalTriangleFailureContract


def main():
    print("=" * 70)
    print("R26-T058: Pascal-Triangle - `generate_pascal_triangle` Failure Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: math/Pascal-Triangle/Pascal-Triangle.py -> generate_pascal_triangle()")
    print("Domain: Absent-result branch (n <= 0), smallest input (n=1), ordinary input (n=4)")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPascalTriangleFailureContract)

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
