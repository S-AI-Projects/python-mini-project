#!/usr/bin/env python3
"""
Focused regression test runner for R26-T059: Spot the Difference print_puzzle complexity scaling.

Usage:
    python3 work/R26-T059/check.py

Requirements:
- Measures scaling on valid inputs across 3 increasing sizes.
- Distinguishes algorithm operations from startup/I/O.
- Reports median and range across 5 repetitions.
- Returns exit code 0 on success, non-zero on failure.
"""

import sys
import os
import time
import io
from pathlib import Path
import unittest
from unittest.mock import patch

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_spot_difference_scaling import TestSpotTheDifferenceScaling, load_module


def run_scaling_benchmark():
    module = load_module()
    sizes = [
        ("Small", 3, 11),
        ("Medium", 10, 25),
        ("Large", 50, 100),
    ]

    print("\n--- Empirical Scaling Benchmark (5 repetitions per size) ---")
    print(f"{'Size':<10} | {'Dimensions (RxC)':<18} | {'Total Chars':<12} | {'Median Time (s)':<16} | {'Range (s)':<14}")
    print("-" * 80)

    for label, r, c in sizes:
        puzzle = {
            "left": ["*" * c for _ in range(r)],
            "right": ["*" * c for _ in range(r)],
            "answer": (1, 1),
        }
        durations = []
        for _ in range(5):
            buf = io.StringIO()
            t0 = time.perf_counter()
            with patch("sys.stdout", buf):
                module.print_puzzle(puzzle)
            t1 = time.perf_counter()
            durations.append(t1 - t0)

        durations.sort()
        median_t = durations[len(durations) // 2]
        rng_t = durations[-1] - durations[0]
        chars = r * c
        print(f"{label:<10} | {f'{r} x {c}':<18} | {chars:<12} | {median_t:<16.6f} | {rng_t:<14.6f}")

    print("-" * 80 + "\n")


def main():
    print("=" * 70)
    print("R26-T059: Spot-the-Difference - `print_puzzle` Complexity Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: games/Spot-the-Difference/Spot-the-Difference.py -> print_puzzle()")
    print("Domain: Input size variables R (rows) and C (cols); Time O(R * C); Space O(C)")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSpotTheDifferenceScaling)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    run_scaling_benchmark()

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
        print("\n✅ ALL REGRESSION TESTS PASSED (scaling metrics recorded)")
        sys.exit(0)


if __name__ == "__main__":
    main()
