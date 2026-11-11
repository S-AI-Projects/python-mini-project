#!/usr/bin/env python3
"""
Verification script for Matrix Determinant contract regression tests.
Loads cases.json, runs each case against determinant(), and prints PASS/FAIL.
Exits with code 0 on full success, or code 1 if any check fails.
"""

import importlib.util
import json
from pathlib import Path
import sys

WORK_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORK_DIR.parent.parent
MAIN_PY = REPO_ROOT / "utilities" / "Matrix-Determinant" / "main.py"
CASES_JSON = WORK_DIR / "cases.json"


def load_determinant_function():
    spec = importlib.util.spec_from_file_location("matrix_determinant_main", MAIN_PY)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module specification from {MAIN_PY}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.determinant


def main():
    if not CASES_JSON.exists():
        print(f"Error: {CASES_JSON} not found.")
        sys.exit(1)

    with CASES_JSON.open("r", encoding="utf-8") as f:
        cases = json.load(f)

    determinant = load_determinant_function()

    total = len(cases)
    passed = 0
    failed = 0

    print("=" * 70)
    print("Matrix Determinant Contract Checks")
    print("=" * 70)

    for idx, case in enumerate(cases, start=1):
        desc = case.get("description", f"Case {idx}")
        inp = case["input"]
        expected = case["expected"]

        actual = None
        error_name = None

        try:
            actual = determinant(inp)
        except ValueError:
            error_name = "ValueError"
            actual = "ValueError"
        except TypeError:
            error_name = "TypeError"
            actual = "TypeError"
        except Exception as exc:
            error_name = type(exc).__name__
            actual = error_name

        is_match = False
        if isinstance(expected, str) and expected in ("ValueError", "TypeError"):
            is_match = (error_name == expected)
        elif isinstance(expected, float):
            is_match = (isinstance(actual, (int, float)) and abs(actual - expected) < 1e-9)
        else:
            is_match = (actual == expected)

        if is_match:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(f"[{status}] {desc}")
        print(f"       Input:    {inp}")
        print(f"       Expected: {expected}")
        print(f"       Actual:   {actual}")

    print("-" * 70)
    print(f"Summary: {passed}/{total} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
