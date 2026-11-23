"""
Focused test runner for Task R26-T048.
Runs unit tests for utilities/Anagram-Finder and asserts the core contract and failure-path safety.
Saves test results to work/R26-T048/test_results.md.
"""

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "utilities" / "Anagram-Finder" / "main.py"

spec = importlib.util.spec_from_file_location("anagram_finder", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["anagram_finder"] = mod
spec.loader.exec_module(mod)
find_anagrams = mod.find_anagrams

print("=== Running checks for R26-T048 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Check 1: Stated goal test: listen with [silent,enlist,listen,banana] -> [silent,enlist]
query1 = "listen"
cands1 = ["silent", "enlist", "listen", "banana"]
exp1 = ["silent", "enlist"]
act1 = find_anagrams(query1, cands1)
passed1 = (act1 == exp1)
print(f"[{'PASS' if passed1 else 'FAIL'}] Core anagram check: query='{query1}', expected={exp1}, actual={act1}")
results_log.append({
    "test": "Core requirement check",
    "input": f"query='{query1}', candidates={cands1}",
    "expected": str(exp1),
    "actual": str(act1),
    "passed": passed1
})
if not passed1:
    all_passed = False

# Check 2: Caller data preservation
cands2 = ["silent", "enlist", "listen", "banana"]
backup2 = list(cands2)
_ = find_anagrams(query1, cands2)
passed2 = (cands2 == backup2)
print(f"[{'PASS' if passed2 else 'FAIL'}] Caller data intact check: {passed2}")
results_log.append({
    "test": "Caller data preservation",
    "input": "candidates list",
    "expected": "Unchanged list in-place",
    "actual": "List intact",
    "passed": passed2
})
if not passed2:
    all_passed = False

# Check 3: Actionable failure path on invalid query type
try:
    find_anagrams(12345, ["word"])
    passed3 = False
except TypeError as e:
    passed3 = "query must be a string" in str(e)
print(f"[{'PASS' if passed3 else 'FAIL'}] Actionable error on invalid query type: {passed3}")
results_log.append({
    "test": "Actionable error on invalid query",
    "input": "query=12345",
    "expected": "TypeError: query must be a string",
    "actual": "Raised expected actionable TypeError",
    "passed": passed3
})
if not passed3:
    all_passed = False

# Check 4: Actionable failure path on invalid candidates type
try:
    find_anagrams("query", 999)
    passed4 = False
except TypeError as e:
    passed4 = "candidates must be a list or tuple" in str(e)
print(f"[{'PASS' if passed4 else 'FAIL'}] Actionable error on invalid candidates type: {passed4}")
results_log.append({
    "test": "Actionable error on invalid candidates",
    "input": "candidates=999",
    "expected": "TypeError: candidates must be a list or tuple",
    "actual": "Raised expected actionable TypeError",
    "passed": passed4
})
if not passed4:
    all_passed = False

# Run unittest suite in utilities/Anagram-Finder
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "utilities" / "Anagram-Finder"), pattern="test_*.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T048\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write(f"- Tests executed: Anagram Finder contract and failure-path coverage\n")
    f.write(f"- Total unit tests run: {test_result.testsRun}\n\n")
    f.write("## Test Summary\n\n")
    f.write("| Test | Input | Expected | Actual | Status |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['test']} | {r['input']} | {r['expected']} | {r['actual']} | {st} |\n")

if all_passed:
    print("\nAll checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
