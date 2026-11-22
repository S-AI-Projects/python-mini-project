#!/usr/bin/env python3
"""
Focused regression test runner for R26-T060: Emoji Memory Game is_browser mutation tests.

Usage:
    python3 work/R26-T060/check.py

Requirements:
- Imports or invokes only the named module / tests.
- Verifies original implementation passes all tests.
- Proves a plausible one-line mutant fails the named assertion.
- Returns exit code 0 on success, non-zero on failure.
"""

import sys
import os
from pathlib import Path
import unittest
from unittest.mock import patch

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_emoji_memory_is_browser import TestEmojiMemoryIsBrowserContract, load_module


def run_mutation_check():
    """Verify that a deliberate mutant fails the exact named assertion."""
    print("\n--- Running Mutation Resistance Verification ---")
    module = load_module()

    # Plausible one-line mutant: inverted equality check
    def mutant_is_browser():
        return sys.platform != "emscripten"

    original_func = module.is_browser
    try:
        module.is_browser = mutant_is_browser
        test_case = TestEmojiMemoryIsBrowserContract("test_browser_platform_detection_emscripten")
        test_case.module = module
        try:
            test_case.test_browser_platform_detection_emscripten()
            print("❌ Mutant unexpectedly passed assertions!")
            return False
        except AssertionError as err:
            print("✅ Mutation successfully detected! The mutant failed 'test_browser_platform_detection_emscripten' as required.")
            print(f"   Assertion failure: {err}")
            return True
    finally:
        module.is_browser = original_func


def main():
    print("=" * 70)
    print("R26-T060: Emoji-Memory-Game - `is_browser` Mutation-Resistant Runner")
    print("=" * 70)
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print("Target: games/Emoji-Memory-Game/Emoji-Memory-Game.py -> is_browser()")
    print("Domain: Emscripten browser platform detection (sys.platform == 'emscripten')")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEmojiMemoryIsBrowserContract)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    mutation_ok = run_mutation_check()

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

    if not result.wasSuccessful() or not mutation_ok:
        print("\n❌ REGRESSION / MUTATION TESTS FAILED")
        for test, trace in result.failures + result.errors:
            print(f"\nFailure in {test}:")
            print(trace)
        sys.exit(1)
    else:
        print("\n✅ ALL REGRESSION TESTS PASSED (Original passed, Mutant failed named assertion)")
        sys.exit(0)


if __name__ == "__main__":
    main()
