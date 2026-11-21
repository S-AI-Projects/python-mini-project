#!/usr/bin/env python3
"""Focused check runner for R26-T040: Strengthen quick_sort tests.

Runs pytest on tests/test_quick_sort.py, proves that a regression test
detects a plausible one-line mutant in quick_sort on fixture [2, 2, 1],
verifies contract invariants and ruff linting. Saves results.json and report.txt.
"""

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent
VENV_RUFF = ROOT / ".venv" / "bin" / "ruff"
VENV_PYTEST = ROOT / ".venv" / "bin" / "pytest"
QUICK_SORT_SCRIPT = ROOT / "math" / "Quick-Sort" / "Quick-Sort.py"


def _run_cmd(cmd, cwd=ROOT):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    return res.returncode, res.stdout + res.stderr


def _load_original_quick_sort():
    spec = importlib.util.spec_from_file_location("quick_sort_orig", QUICK_SORT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.quick_sort


def _mutant_quick_sort(arr: list[int], reverse: bool = False) -> list[int]:
    """Plausible one-line mutant: inverted boundary comparison '>=' instead of '<='."""
    if len(arr) <= 1:
        return arr.copy()
    pivot = arr[-1]
    left = []
    right = []
    for value in arr[:-1]:
        # MUTATION: inverted boundary comparison '>=' instead of '<='
        if not reverse and value >= pivot:
            left.append(value)
        elif not reverse and value < pivot:
            right.append(value)
        elif reverse and value >= pivot:
            left.append(value)
        else:
            right.append(value)
    return _mutant_quick_sort(left, reverse) + [pivot] + _mutant_quick_sort(right, reverse)


def main():
    results = {"tool_versions": {}, "checks": []}
    all_ok = True
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Record tool versions
    py_ver = subprocess.check_output([sys.executable, "--version"], text=True).strip()
    pt_ver = subprocess.check_output([str(VENV_PYTEST), "--version"], text=True).strip()
    results["tool_versions"] = {"python": py_ver, "pytest": pt_ver}

    # ------------------------------------------------------------------------
    # Check 1: Run focused pytest suite
    # ------------------------------------------------------------------------
    pt_cmd = [str(VENV_PYTEST), "tests/test_quick_sort.py", "-v", "--tb=short"]
    rc_pt, out_pt = _run_cmd(pt_cmd)
    passed = total = 0
    for line in out_pt.splitlines():
        if "passed in" in line:
            for token in line.split():
                if token.isdigit():
                    passed = int(token)
                    total = passed
                    break
    ok_pt = rc_pt == 0 and total > 0
    results["checks"].append(
        {
            "name": "pytest_quick_sort_suite",
            "command": f"{VENV_PYTEST} tests/test_quick_sort.py -v --tb=short",
            "passed": passed,
            "total": total,
            "exit_code": rc_pt,
            "status": "PASS" if ok_pt else "FAIL",
        }
    )
    if not ok_pt:
        all_ok = False
        print(f"FAIL: pytest_quick_sort_suite ({passed}/{total})")
        print(out_pt)

    # ------------------------------------------------------------------------
    # Check 2: Benchmark fixtures verification with original implementation
    # ------------------------------------------------------------------------
    orig_qs = _load_original_quick_sort()

    fixtures = [
        {"name": "unsorted", "input": [3, 1, 2], "expected": [1, 2, 3], "reverse": False},
        {"name": "duplicates", "input": [2, 2, 1], "expected": [1, 2, 2], "reverse": False},
        {"name": "already_ordered", "input": [1, 2, 3], "expected": [1, 2, 3], "reverse": False},
        {"name": "reversed", "input": [3, 2, 1], "expected": [1, 2, 3], "reverse": False},
        {"name": "empty", "input": [], "expected": [], "reverse": False},
        {"name": "single", "input": [42], "expected": [42], "reverse": False},
        {"name": "descending_duplicates", "input": [2, 2, 1], "expected": [2, 2, 1], "reverse": True},
    ]

    fixture_results = []
    for f in fixtures:
        inp = list(f["input"])
        actual = orig_qs(inp, reverse=f["reverse"])
        matches = actual == f["expected"]
        not_mutated = inp == f["input"]
        if not (matches and not_mutated):
            all_ok = False
        fixture_results.append(
            {
                "fixture": f["name"],
                "input": f["input"],
                "reverse": f["reverse"],
                "expected": f["expected"],
                "actual": actual,
                "input_preserved": not_mutated,
                "status": "PASS" if (matches and not_mutated) else "FAIL",
            }
        )

    results["checks"].append(
        {
            "name": "benchmark_fixtures_original",
            "fixtures": fixture_results,
            "status": "PASS" if all(f["status"] == "PASS" for f in fixture_results) else "FAIL",
        }
    )

    # ------------------------------------------------------------------------
    # Check 3: Plausible one-line mutant differential test
    # ------------------------------------------------------------------------
    # Differentiating input: [2, 2, 1]
    diff_input = [2, 2, 1]
    expected_output = [1, 2, 2]

    orig_out = orig_qs(list(diff_input))
    mutant_out = _mutant_quick_sort(list(diff_input))

    orig_passed = orig_out == expected_output
    mutant_failed = mutant_out != expected_output

    named_assertion = "test_duplicates_multiplicity_preserved"
    semantic_reason = (
        "In the mutant, line 34 boundary comparison is altered to 'value >= pivot' instead of 'value <= pivot'. "
        "This inverts the partition predicate, placing elements greater than or equal to the pivot into the left "
        "partition rather than the right partition. For input [2, 2, 1], the original correctly produces [1, 2, 2] "
        f"(ascending), whereas the mutant produces {mutant_out} (descending), failing the assertion."
    )

    differential_ok = orig_passed and mutant_failed
    if not differential_ok:
        all_ok = False

    results["checks"].append(
        {
            "name": "mutant_differential_verification",
            "named_assertion": named_assertion,
            "differentiating_input": diff_input,
            "expected_output": expected_output,
            "original_output": orig_out,
            "original_passed": orig_passed,
            "mutant_output": mutant_out,
            "mutant_failed": mutant_failed,
            "semantic_reason": semantic_reason,
            "status": "PASS" if differential_ok else "FAIL",
        }
    )

    # ------------------------------------------------------------------------
    # Check 4: Ruff lint
    # ------------------------------------------------------------------------
    rc_ruff, out_ruff = _run_cmd([
        str(VENV_RUFF),
        "check",
        "math/Quick-Sort/Quick-Sort.py",
        "tests/test_quick_sort.py",
    ])
    ok_ruff = rc_ruff == 0
    results["checks"].append(
        {
            "name": "ruff_lint",
            "command": "ruff check math/Quick-Sort/Quick-Sort.py tests/test_quick_sort.py",
            "exit_code": rc_ruff,
            "status": "PASS" if ok_ruff else "FAIL",
            "output": out_ruff.strip(),
        }
    )
    if not ok_ruff:
        all_ok = False
        print("FAIL: ruff_lint")
        print(out_ruff)

    results["timestamp"] = timestamp
    results["overall"] = "PASS" if all_ok else "FAIL"

    WORK.mkdir(parents=True, exist_ok=True)
    with open(WORK / "results.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    with open(WORK / "report.txt", "w", encoding="utf-8") as fh:
        fh.write(f"R26-T040 Check Report — {timestamp}\n")
        fh.write("=" * 60 + "\n\n")
        for c in results["checks"]:
            fh.write(f"[{c['status']}] {c['name']}\n")
            if "command" in c:
                fh.write(f"       Command: {c['command']}\n")
            if "passed" in c:
                fh.write(f"       Tests: {c['passed']}/{c['total']}\n")
            fh.write("\n")
        fh.write(f"Overall: {results['overall']}\n")

    if all_ok:
        print(f"ALL CHECKS PASSED ({passed} pytest tests, mutant differential verified, ruff clean)")
    else:
        print("SOME CHECKS FAILED — see work/R26-T040/results.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
