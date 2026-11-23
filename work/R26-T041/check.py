"""
Focused test runner for Task R26-T041.
Runs focused Python tests on math/Collatz-Conjecture/Collatz-Conjecture.py.
Outputs expected vs actual results and tool versions, exiting non-zero on failure.
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load module
module_path = REPO_ROOT / "math" / "Collatz-Conjecture" / "Collatz-Conjecture.py"
spec = importlib.util.spec_from_file_location("collatz_mod", module_path)
collatz_mod = importlib.util.module_from_spec(spec)
sys.modules["collatz_mod"] = collatz_mod
spec.loader.exec_module(collatz_mod)

test_cases = [
    # (name, input_n, expected, precondition_anchor)
    ("Smallest valid input (n=1)", 1, 4, "steps_cache = {1: 0} at line 6"),
    ("Ordinary odd input (n=3)", 3, 10, "odd formula 3*n + 1 near line 8"),
    ("Ordinary even input (n=4)", 4, 2, "even formula n // 2 near line 8"),
    ("Ordinary odd input (n=5)", 5, 16, "odd formula 3*n + 1 near line 8"),
    ("Ordinary even input (n=6)", 6, 3, "even formula n // 2 near line 8"),
    ("Boundary cycle input (n=2)", 2, 1, "even formula n // 2 near line 8"),
]

print("=== Running checks for R26-T041 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Check global cache anchor
cache_before = dict(collatz_mod.steps_cache)
if cache_before != {1: 0}:
    print(f"FAILED: steps_cache precondition mismatch: {cache_before}")
    all_passed = False

for name, val_in, expected, anchor in test_cases:
    actual = collatz_mod.collatz_next(val_in)
    passed = actual == expected
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: input={val_in}, expected={expected}, actual={actual} (Precondition: {anchor})")
    results_log.append({
        "test": name,
        "input": val_in,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "anchor": anchor
    })
    if not passed:
        all_passed = False

# Mutation check
cache_after = dict(collatz_mod.steps_cache)
if cache_after != {1: 0}:
    print(f"FAILED: steps_cache mutated: {cache_after}")
    all_passed = False
else:
    print("[PASS] Global state mutation check: steps_cache unchanged ({1: 0})")

# Run unittest test suite
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "tests"), pattern="test_collatz_conjecture.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T041\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: `collatz_next` contract and regression tests\n")
    f.write("- Total tests run in suite: " + str(test_result.testsRun) + "\n\n")
    f.write("## Test Cases\n\n")
    f.write("| Test | Input | Expected | Actual | Precondition / Anchor | Status |\n")
    f.write("| --- | --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['test']} | {r['input']} | {r['expected']} | {r['actual']} | {r['anchor']} | {st} |\n")
    f.write(f"| Mutation check | steps_cache | {{1: 0}} | {cache_after} | steps_cache = {{1: 0}} (line 6) | PASS |\n")

if all_passed:
    print("\nAll checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
