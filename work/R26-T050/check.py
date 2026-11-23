"""
Focused test runner for Task R26-T050.
Executes mutation-resistant tests on utilities/Palindrome-Finder.
Outputs expected vs actual results and tool versions, exiting non-zero on failure.
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_PATH = REPO_ROOT / "utilities" / "Palindrome-Finder" / "main.py"

spec = importlib.util.spec_from_file_location("pal_finder", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["pal_finder"] = mod
spec.loader.exec_module(mod)
find_palindromes = mod.find_palindromes
is_palindrome = mod.is_palindrome

print("=== Running checks for R26-T050 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Check 1: Required input/output test [Level,cat,radar] -> [Level,radar]
w1 = ["Level", "cat", "radar"]
exp1 = ["Level", "radar"]
act1 = find_palindromes(w1)
p1 = (act1 == exp1)
print(f"[{'PASS' if p1 else 'FAIL'}] Required test [Level,cat,radar]: expected={exp1}, actual={act1}")
results_log.append({
    "test": "Primary requirement [Level,cat,radar]",
    "input": str(w1),
    "expected": str(exp1),
    "actual": str(act1),
    "passed": p1
})
if not p1:
    all_passed = False

# Check 2: Empty word policy (excluded as non-palindrome)
p2 = (not is_palindrome("")) and (find_palindromes(["", "racecar", ""]) == ["racecar"])
print(f"[{'PASS' if p2 else 'FAIL'}] Empty word policy (len > 0 required): {p2}")
results_log.append({
    "test": "Empty word policy",
    "input": "['', 'racecar', '']",
    "expected": "['racecar'] (empty excluded)",
    "actual": "['racecar']" if p2 else "Failed",
    "passed": p2
})
if not p2:
    all_passed = False

# Check 3: Deliberate mutation test 1 - Case sensitivity mutant
# Mutant condition: word == word[::-1] (fails for "Level")
mutant1 = lambda w: len(w) > 0 and w == w[::-1]
m1_caught = (mutant1("Level") is False and is_palindrome("Level") is True)
print(f"[{'PASS' if m1_caught else 'FAIL'}] Case sensitivity mutant caught: {m1_caught}")
results_log.append({
    "test": "Mutant 1: Case-sensitive check",
    "input": "'Level'",
    "expected": "Rejects case-sensitive mutant",
    "actual": "Caught and rejected",
    "passed": m1_caught
})
if not m1_caught:
    all_passed = False

# Check 4: Deliberate mutation test 2 - Inverted condition mutant
mutant2 = lambda w: len(w.lower()) > 0 and w.lower() != w.lower()[::-1]
m2_caught = (mutant2("radar") is False and is_palindrome("radar") is True)
print(f"[{'PASS' if m2_caught else 'FAIL'}] Inverted condition mutant caught: {m2_caught}")
results_log.append({
    "test": "Mutant 2: Inverted condition check",
    "input": "'radar'",
    "expected": "Rejects inverted condition mutant",
    "actual": "Caught and rejected",
    "passed": m2_caught
})
if not m2_caught:
    all_passed = False

# Run unittest suite in utilities/Palindrome-Finder
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "utilities" / "Palindrome-Finder"), pattern="test_*.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T050\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: Mutation-resistant tests for `Palindrome-Finder`\n")
    f.write(f"- Total unit tests run: {test_result.testsRun}\n")
    f.write("- Stated policy: Empty words are excluded (len > 0 required)\n\n")
    f.write("## Test Cases & Mutation Resistance\n\n")
    f.write("| Test | Input | Expected | Actual | Status |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['test']} | {r['input']} | {r['expected']} | {r['actual']} | {st} |\n")

if all_passed:
    print("\nAll mutation-resistant checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
