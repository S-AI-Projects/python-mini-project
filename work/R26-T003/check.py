"""Verification script for Simple Interest Calculator cases.
Loads cases.json, calls calculate_simple_interest, and verifies results.
"""

from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
CASES_FILE = BASE_DIR / "cases.json"
MAIN_FILE = REPO_ROOT / "utilities" / "Simple-Interest-Calculator" / "main.py"

# Dynamically import calculate_simple_interest from main.py
spec = importlib.util.spec_from_file_location("simple_interest_main", MAIN_FILE)
if spec is None or spec.loader is None:
    sys.stderr.write(f"❌ Failed to load spec from {MAIN_FILE}\n")
    sys.exit(1)
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)
calculate_simple_interest = main_mod.calculate_simple_interest


def main() -> None:
    if not CASES_FILE.exists():
        sys.stderr.write(f"❌ Cases file not found: {CASES_FILE}\n")
        sys.exit(1)

    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    all_passed = True
    print(f"Running verification on {len(cases)} test cases from {CASES_FILE.name}:")
    print("-" * 70)

    for i, case in enumerate(cases, start=1):
        p_str = case["principal"]
        r_str = case["rate"]
        t_str = case["years"]
        expected_str = case["expected"]
        expected_dec = Decimal(expected_str)

        try:
            actual_dec = calculate_simple_interest(p_str, r_str, t_str)
        except Exception as exc:
            print(f"[{i:02d}] FAIL: P={p_str}, R={r_str}, T={t_str} -> Raised exception: {exc}")
            all_passed = False
            continue

        if actual_dec == expected_dec:
            print(
                f"[{i:02d}] PASS: P={p_str}, R={r_str}, T={t_str} | "
                f"Expected={expected_dec} | Actual={actual_dec}"
            )
        else:
            print(
                f"[{i:02d}] FAIL: P={p_str}, R={r_str}, T={t_str} | "
                f"Expected={expected_dec} | Actual={actual_dec}"
            )
            all_passed = False

    print("-" * 70)
    if all_passed:
        print("✓ All test cases passed successfully.")
        sys.exit(0)
    else:
        print("❌ One or more test cases failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
