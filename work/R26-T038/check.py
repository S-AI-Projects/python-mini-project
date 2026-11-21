#!/usr/bin/env python3
"""Focused check runner for R26-T038: Roman-Numerals failure-path coverage.

Executes native unittest discovery, programmatic failure-path verification,
registry integrity checks, and ruff linting. Saves results.json and report.txt.
Exits non-zero on any assertion or check failure.
"""

import json
import subprocess
import sys
import tempfile
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
        "utilities/Roman-Numerals",
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
            "command": "python3 -m unittest discover -s utilities/Roman-Numerals -p 'test_*.py' -v",
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
    # Check 2: Benchmark and failure-path input/expected/actual verification
    # ------------------------------------------------------------------------
    sys.path.insert(0, str(ROOT / "utilities" / "Roman-Numerals"))
    import main as roman_mod

    benchmark_cases = [
        (1, "I"),
        (4, "IV"),
        (9, "IX"),
        (58, "LVIII"),
        (1994, "MCMXCIV"),
        (3999, "MMMCMXCIX"),
    ]
    benchmark_results = []
    for num, expected in benchmark_cases:
        actual = roman_mod.to_roman(num)
        matches = actual == expected
        if not matches:
            all_ok = False
        benchmark_results.append(
            {
                "input": num,
                "expected": expected,
                "actual": actual,
                "match": matches,
            }
        )

    # Failure-path boundary cases
    failure_cases = [
        {"input": 0, "expected_error": "ValueError"},
        {"input": -1, "expected_error": "ValueError"},
        {"input": 4000, "expected_error": "ValueError"},
        {"input": 3.14, "expected_error": "TypeError"},
        {"input": "1994", "expected_error": "TypeError"},
        {"input": True, "expected_error": "TypeError"},
    ]
    failure_results = []
    for fc in failure_cases:
        inp = fc["input"]
        exp_err = fc["expected_error"]
        caught = None
        actionable = False
        msg = ""
        try:
            roman_mod.to_roman(inp)
        except Exception as exc:
            caught = type(exc).__name__
            msg = str(exc)
            actionable = "Action:" in msg
        matches = caught == exp_err and actionable
        if not matches:
            all_ok = False
        failure_results.append(
            {
                "input": repr(inp),
                "expected_exception": exp_err,
                "actual_exception": caught,
                "actionable_message": actionable,
                "message": msg,
                "status": "PASS" if matches else "FAIL",
            }
        )

    # Failure-path data-integrity proof (caller data intact)
    caller_list = [1, 4, 0, 9]
    original_list = list(caller_list)
    caller_intact = False
    try:
        roman_mod.convert_many(caller_list)
    except ValueError:
        caller_intact = caller_list == original_list
    if not caller_intact:
        all_ok = False

    # Failure-path file-integrity proof (target file not created on error)
    file_intact = False
    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "source.txt"
        dst = Path(tmpdir) / "target.txt"
        src.write_text("1\n4\n-99\n58\n", encoding="utf-8")
        try:
            roman_mod.convert_file(src, dst)
        except ValueError:
            file_intact = not dst.exists()
    if not file_intact:
        all_ok = False

    results["checks"].append(
        {
            "name": "functional_and_failure_path_verification",
            "benchmarks": benchmark_results,
            "failure_paths": failure_results,
            "caller_data_intact_on_failure": caller_intact,
            "caller_file_intact_on_failure": file_intact,
            "status": "PASS" if (caller_intact and file_intact and all(b["match"] for b in benchmark_results) and all(f["status"] == "PASS" for f in failure_results)) else "FAIL",
        }
    )

    # ------------------------------------------------------------------------
    # Check 3: Ruff lint
    # ------------------------------------------------------------------------
    rc_ruff, out_ruff = _run_cmd([
        str(VENV_RUFF),
        "check",
        "utilities/Roman-Numerals/main.py",
        "utilities/Roman-Numerals/test_main.py",
    ])
    ok_ruff = rc_ruff == 0
    results["checks"].append(
        {
            "name": "ruff_lint",
            "command": "ruff check utilities/Roman-Numerals/main.py utilities/Roman-Numerals/test_main.py",
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
    # Check 4: Registry integrity
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
        fh.write(f"R26-T038 Check Report — {timestamp}\n")
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
        print(f"ALL CHECKS PASSED ({test_count} unittest tests, all benchmarks and failure paths verified, ruff clean)")
    else:
        print("SOME CHECKS FAILED — see work/R26-T038/results.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
