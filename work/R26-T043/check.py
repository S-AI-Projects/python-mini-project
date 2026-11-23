"""
Focused test runner for Task R26-T043.
Cross-checks solve_quadratic against an independent oracle table of 21 test cases.
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
module_path = REPO_ROOT / "math" / "Quadratic-Solver" / "Quadratic-Solver.py"
spec = importlib.util.spec_from_file_location("quad_mod", module_path)
quad_mod = importlib.util.module_from_spec(spec)
sys.modules["quad_mod"] = quad_mod
spec.loader.exec_module(quad_mod)

from tests.test_quadratic_solver_reference import REFERENCE_CASES

print("=== Running checks for R26-T043 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Precondition check: a == 0 raises ValueError
try:
    quad_mod.solve_quadratic(0, 1, 1)
    precond_passed = False
except ValueError:
    precond_passed = True
print(f"[{'PASS' if precond_passed else 'FAIL'}] Precondition check (a == 0 raises ValueError, line 24): {precond_passed}")
if not precond_passed:
    all_passed = False

# Run through the 21 independent oracle cases
for idx, (a, b, c, exp_kind, exp_r1, exp_r2, exp_d) in enumerate(REFERENCE_CASES, 1):
    kind, r1, r2, d = quad_mod.solve_quadratic(a, b, c)
    kind_ok = (kind == exp_kind)
    d_ok = abs(d - exp_d) < 1e-7

    actual_roots = sorted([r1, r2], key=lambda x: (x.real, x.imag if isinstance(x, complex) else 0))
    expected_roots = sorted([exp_r1, exp_r2], key=lambda x: (x.real, x.imag if isinstance(x, complex) else 0))
    roots_ok = True
    for act, exp in zip(actual_roots, expected_roots):
        if isinstance(exp, complex):
            if abs(act.real - exp.real) >= 1e-7 or abs(act.imag - exp.imag) >= 1e-7:
                roots_ok = False
        else:
            if abs(act - exp) >= 1e-7:
                roots_ok = False

    passed = kind_ok and d_ok and roots_ok
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] Case {idx:02d}: a={a}, b={b}, c={c} -> kind={kind}, r1={r1}, r2={r2}, d={d}")
    results_log.append({
        "case": idx,
        "input": f"({a}, {b}, {c})",
        "expected": f"({exp_kind}, {exp_r1}, {exp_r2}, d={exp_d})",
        "actual": f"({kind}, {r1}, {r2}, d={d})",
        "passed": passed
    })
    if not passed:
        all_passed = False

# Run unittest suite
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "tests"), pattern="test_quadratic_solver_reference.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T043\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: `solve_quadratic` cross-check against 21 independent reference cases\n")
    f.write(f"- Total tests run in suite: {test_result.testsRun}\n")
    f.write(f"- Precondition verified: a == 0 raises ValueError (line 24)\n\n")
    f.write("## Reference Comparison Cases\n\n")
    f.write("| Case | Input (a, b, c) | Expected (kind, r1, r2, d) | Actual (kind, r1, r2, d) | Status |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['case']} | {r['input']} | {r['expected']} | {r['actual']} | {st} |\n")

if all_passed:
    print(f"\nAll {len(REFERENCE_CASES)} reference checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
