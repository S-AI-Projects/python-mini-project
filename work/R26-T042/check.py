"""
Focused test runner for Task R26-T042.
Executes boundary tests for initialize_file in utilities/Budget-Tracker/budget_tracker.py.
Outputs expected vs actual results and tool versions, exiting non-zero on failure.
"""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load module
module_path = REPO_ROOT / "utilities" / "Budget-Tracker" / "budget_tracker.py"
spec = importlib.util.spec_from_file_location("budget_mod", module_path)
budget_mod = importlib.util.module_from_spec(spec)
sys.modules["budget_mod"] = budget_mod
spec.loader.exec_module(budget_mod)

print("=== Running checks for R26-T042 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Check anchor FIELDNAMES at line 16
expected_fields = ["id", "date", "type", "category", "description", "amount"]
actual_fields = budget_mod.FIELDNAMES
anchor_passed = actual_fields == expected_fields
print(f"[{'PASS' if anchor_passed else 'FAIL'}] Anchor FIELDNAMES (line 16): expected={expected_fields}, actual={actual_fields}")
results_log.append({
    "test": "Anchor FIELDNAMES check",
    "input": "FIELDNAMES at line 16",
    "expected": str(expected_fields),
    "actual": str(actual_fields),
    "passed": anchor_passed
})
if not anchor_passed:
    all_passed = False

# Boundary 1: Smallest valid input / Non-existent file creation
with tempfile.TemporaryDirectory() as tmpdir:
    test_file_new = os.path.join(tmpdir, "test_new.csv")
    budget_mod.initialize_file(test_file_new)
    file_created = os.path.exists(test_file_new)
    if file_created:
        with open(test_file_new, "r", encoding="utf-8") as f:
            header_line = f.readline().strip()
    else:
        header_line = ""
    expected_header = ",".join(expected_fields)
    b1_passed = file_created and (header_line == expected_header)
    print(f"[{'PASS' if b1_passed else 'FAIL'}] Boundary 1 (Non-existent file creation): created={file_created}, header='{header_line}'")
    results_log.append({
        "test": "Boundary 1: Non-existent file creation",
        "input": "Non-existent path",
        "expected": expected_header,
        "actual": header_line,
        "passed": b1_passed
    })
    if not b1_passed:
        all_passed = False

# Boundary 2: Ordinary input / Existing file idempotency
with tempfile.TemporaryDirectory() as tmpdir:
    test_file_exist = os.path.join(tmpdir, "test_exist.csv")
    sample_content = "id,date,type,category,description,amount\n1,2026-11-23,income,Salary,Monthly,5000\n"
    with open(test_file_exist, "w", encoding="utf-8") as f:
        f.write(sample_content)

    budget_mod.initialize_file(test_file_exist)

    with open(test_file_exist, "r", encoding="utf-8") as f:
        actual_content = f.read()

    b2_passed = actual_content == sample_content
    print(f"[{'PASS' if b2_passed else 'FAIL'}] Boundary 2 (Existing file idempotency): content preserved={b2_passed}")
    results_log.append({
        "test": "Boundary 2: Existing file idempotency",
        "input": "Existing file with rows",
        "expected": "Unchanged existing content",
        "actual": "Content preserved" if b2_passed else "Content altered",
        "passed": b2_passed
    })
    if not b2_passed:
        all_passed = False

# Run unittest suite
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "tests"), pattern="test_budget_tracker_boundary.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T042\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: `initialize_file` boundary and idempotency tests\n")
    f.write("- Total tests run in suite: " + str(test_result.testsRun) + "\n\n")
    f.write("## Test Cases & Boundary Verification\n\n")
    f.write("| Test | Input / Anchor | Expected | Actual | Status |\n")
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
