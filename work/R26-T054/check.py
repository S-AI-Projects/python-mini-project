#!/usr/bin/env python3
"""
Focused regression test runner for R26-T054: Text-to-Morse _sleep_ms function.

Usage:
    python3 work/R26-T054/check.py

Requirements:
- Imports or invokes only the named module / tests.
- Mocks external I/O and time.sleep.
- Tests properties over 100 bounded valid cases with fixed seed.
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

from tests.test_text_to_morse_sleep import TestSleepMsInvariant


def main():
    print("=" * 70)
    print("R26-T054: Text-to-Morse - `_sleep_ms` Invariant Property Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: utilities/Text-to-Morse/Text-to-Morse.py -> _sleep_ms()")
    print("Domain: ms >= 0 -> seconds = ms / 1000.0 (100 bounded property samples)")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSleepMsInvariant)

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
        print("\n✅ ALL REGRESSION TESTS PASSED (including 100 invariant cases)")
        sys.exit(0)


if __name__ == "__main__":
    main()
