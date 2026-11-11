"""
Independent verification script for Password Strength Meter.
Loads cases.json, imports check_password and count_satisfied via
importlib.util.spec_from_file_location, compares actual vs expected,
and prints PASS/FAIL with details. Exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "utilities" / "Password-Strength-Meter" / "main.py"
CASES_PATH = Path(__file__).resolve().parent / "cases.json"

spec = importlib.util.spec_from_file_location("password_strength_meter_main", MODULE_PATH)
if spec is None or spec.loader is None:
    sys.stderr.write(f"Cannot load module from {MODULE_PATH}\n")
    sys.exit(1)
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

check_password = main_mod.check_password
count_satisfied = main_mod.count_satisfied


def main() -> int:
    if not CASES_PATH.exists():
        sys.stderr.write(f"cases.json not found at {CASES_PATH}\n")
        return 1

    with open(CASES_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    all_passed = True
    print(f"Running independent verification against {len(cases)} cases in {CASES_PATH.name}...")
    print("=" * 60)

    for i, case in enumerate(cases, start=1):
        raw_input = case["input"]
        expected = case["expected"]

        actual_conditions = check_password(raw_input)
        actual_count = count_satisfied(actual_conditions)
        actual = {**actual_conditions, "count": actual_count}

        passed = actual == expected
        status = "PASS" if passed else "FAIL"

        print(f"Case {i:2d} [{status}]: input={raw_input!r}")
        if not passed:
            all_passed = False
            print(f"  Expected: {expected}")
            print(f"  Actual  : {actual}")

    print("=" * 60)
    if all_passed:
        print("All test cases PASSED successfully.")
        return 0
    else:
        print("One or more test cases FAILED.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
