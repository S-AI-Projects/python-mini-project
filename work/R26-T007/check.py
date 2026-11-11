#!/usr/bin/env python3
"""Focused independent checker for R26-T007: Merge Sort runnable example."""

import doctest
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "math" / "Merge-Sort" / "Merge-Sort.py"
CASES_FILE = Path(__file__).resolve().parent / "cases.json"
TEST_FILE = REPO_ROOT / "tests" / "test_merge_sort.py"


def main():
    print("=== Running R26-T007 Independent Checker ===")

    # 1. Load target module dynamically
    spec = importlib.util.spec_from_file_location("merge_sort_module", TARGET_FILE)
    if spec is None or spec.loader is None:
        print("[FAIL] Could not load spec for Merge-Sort.py")
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    merge_sort = getattr(mod, "merge_sort", None)
    if not callable(merge_sort):
        print("[FAIL] merge_sort function not found in module")
        sys.exit(1)

    # 2. Verify doctest with explicit namespace containing merge_sort
    print("--- Verifying Docstring Runnable Examples via Doctest ---")
    finder = doctest.DocTestFinder()
    tests = finder.find(merge_sort, globs={"merge_sort": merge_sort})
    if not tests:
        print("[FAIL] No doctests found in merge_sort docstring")
        sys.exit(1)

    runner = doctest.DocTestRunner(verbose=False)
    for t in tests:
        runner.run(t)
    if runner.failures != 0 or runner.tries == 0:
        print(f"[FAIL] Doctest failed: {runner.failures} failures out of {runner.tries} tries")
        sys.exit(1)
    print(f"[PASS] Doctests passed ({runner.tries} example(s) verified).")

    # 3. Load fixtures from cases.json and verify outputs and immutability
    print("--- Verifying Required Fixtures from cases.json ---")
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    for case in cases:
        inp = list(case["input"])
        rev = case["reverse"]
        exp = case["expected"]
        orig = list(inp)
        res = merge_sort(inp, reverse=rev)
        if res != exp:
            print(f"[FAIL] Case {case['id']} ({case['description']}): expected {exp}, got {res}")
            sys.exit(1)
        if inp != orig:
            print(f"[FAIL] Case {case['id']}: input was mutated!")
            sys.exit(1)
        print(f"[PASS] Case {case['id']}: {case['description']} -> {res}")

    # 4. Run pytest suite and propagate result
    print("--- Running Pytest Suite ---")
    cmd = ["python3", "-m", "pytest", str(TEST_FILE), "-v"]
    print(f"Command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)

    match = re.search(r"(\d+)\s+passed", proc.stdout)
    passed_count = int(match.group(1)) if match else 0
    print(f"Tests passed count: {passed_count}")

    if proc.returncode != 0 or passed_count == 0:
        print(f"[FAIL] Pytest failed or 0 tests passed (code={proc.returncode})")
        sys.exit(1)

    print("\nALL R26-T007 CHECKS PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
