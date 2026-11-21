#!/usr/bin/env python3
"""Focused check runner for R26-T039: Word-Counter complexity experiment.

Executes native unittest discovery, programmatic benchmark verification,
bounded work complexity experiments at three sizes, registry integrity checks,
and ruff linting. Saves results.json and report.txt. Exits non-zero on failure.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent
VENV_RUFF = ROOT / ".venv" / "bin" / "ruff"
VENV_PYTEST = ROOT / ".venv" / "bin" / "pytest"


def _run_cmd(cmd, cwd=ROOT):
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    return res.returncode, res.stdout + res.stderr


def main():
    results = {"tool_versions": {}, "checks": []}
    all_ok = True
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Record tool versions
    py_ver = subprocess.check_output([sys.executable, "--version"], text=True).strip()
    results["tool_versions"]["python"] = py_ver

    # ------------------------------------------------------------------------
    # Check 1: Native unittest discovery
    # ------------------------------------------------------------------------
    unittest_cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "utilities/Word-Counter",
        "-p",
        "test_*.py",
        "-v",
    ]
    rc1, out1 = _run_cmd(unittest_cmd)
    test_count = 0
    for line in out1.splitlines():
        if "Ran " in line and " tests in" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "Ran" and i + 1 < len(parts):
                    try:
                        test_count = int(parts[i + 1])
                    except ValueError:
                        pass
    ok1 = rc1 == 0 and test_count > 0
    results["checks"].append(
        {
            "name": "native_unittest_discovery",
            "command": "python3 -m unittest discover -s utilities/Word-Counter -p 'test_*.py' -v",
            "test_count": test_count,
            "exit_code": rc1,
            "status": "PASS" if ok1 else "FAIL",
            "output_summary": out1.splitlines()[-1] if out1.splitlines() else "",
        }
    )
    if not ok1:
        all_ok = False
        print(f"FAIL: native_unittest_discovery (rc={rc1})")
        print(out1)

    # ------------------------------------------------------------------------
    # Check 2: Core contract benchmark inputs/expected/actual
    # ------------------------------------------------------------------------
    sys.path.insert(0, str(ROOT / "utilities" / "Word-Counter"))
    import main as word_mod

    benchmarks = [
        {
            "input": "Tea, tea! coffee",
            "expected": {"tea": 2, "coffee": 1},
        },
        {
            "input": "",
            "expected": {},
        },
        {
            "input": "   \n\t  ",
            "expected": {},
        },
        {
            "input": ",,, !!! ...",
            "expected": {},
        },
        {
            "input": "Apple, apple; banana! BANANA... cherry",
            "expected": {"apple": 2, "banana": 2, "cherry": 1},
        },
    ]

    bench_results = []
    for b in benchmarks:
        actual = word_mod.count_words(b["input"])
        matches = actual == b["expected"]
        if not matches:
            all_ok = False
        bench_results.append(
            {
                "input": b["input"],
                "expected": b["expected"],
                "actual": actual,
                "status": "PASS" if matches else "FAIL",
            }
        )

    results["checks"].append(
        {
            "name": "core_contract_benchmarks",
            "cases": bench_results,
            "status": "PASS" if all(c["status"] == "PASS" for c in bench_results) else "FAIL",
        }
    )

    # ------------------------------------------------------------------------
    # Check 3: Bounded work complexity experiment at three sizes
    # ------------------------------------------------------------------------
    sizes = (100, 1000, 10000)
    exp_data = word_mod.run_complexity_experiment(sizes)
    linear_scaling = (
        len(exp_data) == 3
        and exp_data[0]["unique_words_found"] == 10
        and exp_data[1]["unique_words_found"] == 100
        and exp_data[2]["unique_words_found"] == 1000
    )
    if not linear_scaling:
        all_ok = False

    results["checks"].append(
        {
            "name": "complexity_experiment_three_sizes",
            "sizes_evaluated": list(sizes),
            "measurements": exp_data,
            "linear_work_verified": linear_scaling,
            "status": "PASS" if linear_scaling else "FAIL",
        }
    )

    # ------------------------------------------------------------------------
    # Check 4: Ruff lint
    # ------------------------------------------------------------------------
    rc_ruff, out_ruff = _run_cmd([
        str(VENV_RUFF),
        "check",
        "utilities/Word-Counter/main.py",
        "utilities/Word-Counter/test_main.py",
    ])
    ok_ruff = rc_ruff == 0
    results["checks"].append(
        {
            "name": "ruff_lint",
            "command": "ruff check utilities/Word-Counter/main.py utilities/Word-Counter/test_main.py",
            "exit_code": rc_ruff,
            "status": "PASS" if ok_ruff else "FAIL",
            "output": out_ruff.strip(),
        }
    )
    if not ok_ruff:
        all_ok = False
        print("FAIL: ruff_lint")
        print(out_ruff)

    # ------------------------------------------------------------------------
    # Check 5: Registry integrity
    # ------------------------------------------------------------------------
    rc_reg, out_reg = _run_cmd([str(VENV_PYTEST), "tests/test_registry_integrity.py"])
    ok_reg = rc_reg == 0
    results["checks"].append(
        {
            "name": "registry_integrity",
            "command": "pytest tests/test_registry_integrity.py",
            "exit_code": rc_reg,
            "status": "PASS" if ok_reg else "FAIL",
        }
    )
    if not ok_reg:
        all_ok = False
        print("FAIL: registry_integrity")
        print(out_reg)

    results["timestamp"] = timestamp
    results["overall"] = "PASS" if all_ok else "FAIL"

    WORK.mkdir(parents=True, exist_ok=True)
    with open(WORK / "results.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    with open(WORK / "report.txt", "w", encoding="utf-8") as fh:
        fh.write(f"R26-T039 Check Report — {timestamp}\n")
        fh.write("=" * 60 + "\n\n")
        for c in results["checks"]:
            fh.write(f"[{c['status']}] {c['name']}\n")
            if "command" in c:
                fh.write(f"       Command: {c['command']}\n")
            if "test_count" in c:
                fh.write(f"       Tests: {c['test_count']}\n")
            fh.write("\n")
        fh.write(f"Overall: {results['overall']}\n")

    if all_ok:
        print(f"ALL CHECKS PASSED ({test_count} unittest tests, complexity experiment verified, ruff clean)")
    else:
        print("SOME CHECKS FAILED — see work/R26-T039/results.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
