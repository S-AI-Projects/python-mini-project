#!/usr/bin/env python3
"""Focused check runner for R26-T036.

Runs the _build_namespace tests and the existing scientific-calculator tests,
then writes results.json and report.txt.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent
VENV_PYTEST = ROOT / ".venv" / "bin" / "pytest"

os.environ["MPLBACKEND"] = "Agg"


def _run(label, test_path):
    """Run pytest on *test_path*; return (passed, total, returncode, output)."""
    cmd = [str(VENV_PYTEST), str(test_path), "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = result.stdout + result.stderr
    # Parse counts from pytest summary line like "18 passed"
    passed = total = 0
    for line in output.splitlines():
        if "passed" in line:
            for token in line.split():
                if token.isdigit():
                    passed = int(token)
                    total = passed
                    break
    return passed, total, result.returncode, output


def main():
    results = {"tool_versions": {}, "checks": []}

    # Record tool versions
    py_ver = subprocess.check_output([sys.executable, "--version"], text=True).strip()
    pt_ver = subprocess.check_output(
        [str(VENV_PYTEST), "--version"], text=True
    ).strip()
    results["tool_versions"] = {"python": py_ver, "pytest": pt_ver}

    all_ok = True
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Check 1: _build_namespace focused tests (new)
    p, t, rc, out = _run(
        "build_namespace_tests", ROOT / "tests" / "test_build_namespace.py"
    )
    ok1 = rc == 0 and t > 0
    results["checks"].append(
        {
            "name": "test_build_namespace",
            "command": f"{VENV_PYTEST} tests/test_build_namespace.py -v --tb=short",
            "passed": p,
            "total": t,
            "exit_code": rc,
            "status": "PASS" if ok1 else "FAIL",
        }
    )
    if not ok1:
        all_ok = False
        print(f"FAIL: test_build_namespace ({p}/{t})")
        print(out)

    # Check 2: Existing scientific calculator tests (regression)
    p2, t2, rc2, out2 = _run(
        "existing_tests", ROOT / "tests" / "test_scientific_calculator.py"
    )
    ok2 = rc2 == 0 and t2 > 0
    results["checks"].append(
        {
            "name": "test_scientific_calculator_regression",
            "command": f"{VENV_PYTEST} tests/test_scientific_calculator.py -v --tb=short",
            "passed": p2,
            "total": t2,
            "exit_code": rc2,
            "status": "PASS" if ok2 else "FAIL",
        }
    )
    if not ok2:
        all_ok = False
        print(f"FAIL: test_scientific_calculator_regression ({p2}/{t2})")
        print(out2)

    # Check 3: ruff lint
    ruff = ROOT / ".venv" / "bin" / "ruff"
    target = (
        ROOT
        / "math"
        / "Scientific-Graphing-Calculator"
        / "Scientific-Graphing-Calculator.py"
    )
    ruff_rc = subprocess.run(
        [str(ruff), "check", str(target), str(ROOT / "tests" / "test_build_namespace.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    ok3 = ruff_rc.returncode == 0
    results["checks"].append(
        {
            "name": "ruff_lint",
            "command": f"{ruff} check <source> <tests>",
            "exit_code": ruff_rc.returncode,
            "status": "PASS" if ok3 else "FAIL",
            "output": ruff_rc.stdout.strip(),
        }
    )
    if not ok3:
        all_ok = False
        print(f"FAIL: ruff lint")
        print(ruff_rc.stdout)

    results["timestamp"] = timestamp
    results["overall"] = "PASS" if all_ok else "FAIL"

    # Write results
    WORK.mkdir(parents=True, exist_ok=True)
    with open(WORK / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Write report
    with open(WORK / "report.txt", "w") as f:
        f.write(f"R26-T036 Check Report — {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        for c in results["checks"]:
            f.write(f"[{c['status']}] {c['name']}\n")
            f.write(f"       Command: {c['command']}\n")
            if "passed" in c:
                f.write(f"       Tests: {c['passed']}/{c['total']}\n")
            f.write("\n")
        f.write(f"Overall: {results['overall']}\n")

    if all_ok:
        print(f"ALL CHECKS PASSED ({results['checks'][0]['passed']}+"
              f"{results['checks'][1]['passed']} tests, ruff clean)")
    else:
        print("SOME CHECKS FAILED — see work/R26-T036/results.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
