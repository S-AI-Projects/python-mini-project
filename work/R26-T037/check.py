#!/usr/bin/env python3
"""Focused check runner for R26-T037.

Runs the FLAMES-Game worked example and contract tests,
records tool versions, inputs, expected vs actual results,
and writes results.json and report.txt. Exits non-zero on failure.
"""

import io
import json
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent.parent
VENV_PYTEST = ROOT / ".venv" / "bin" / "pytest"
VENV_RUFF = ROOT / ".venv" / "bin" / "ruff"


def _run_pytest(test_path):
    """Run pytest on *test_path*; return (passed, total, returncode, output)."""
    cmd = [str(VENV_PYTEST), str(test_path), "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = result.stdout + result.stderr
    passed = total = 0
    for line in output.splitlines():
        if "passed" in line:
            for token in line.split():
                if token.isdigit():
                    passed = int(token)
                    total = passed
                    break
    return passed, total, result.returncode, output


def _run_native_worked_example_check():
    """Execute the worked example directly via python import with mocked I/O.

    Inputs:
      - Smallest valid: name1="a", name2="b", choice="n"
      - Ordinary input: name1="alex", name2="emma", choice="n"

    Asserts:
      - Correct intermediate variables (total_len, matched_chars, score, result)
      - Correct displayed output substrings
    """
    import importlib.util

    script_path = ROOT / "games" / "FLAMES-Game" / "FLAMES-Game.py"
    spec = importlib.util.spec_from_file_location("flames_game_native", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # 1. Smallest valid input
    stdout_buf1 = io.StringIO()
    with patch("builtins.input", side_effect=["a", "b", "n"]), patch("sys.stdout", stdout_buf1):
        mod.main()
    out1 = stdout_buf1.getvalue()

    assert mod.original_name1 == "a", f"Expected 'a', got {mod.original_name1}"
    assert mod.original_name2 == "b", f"Expected 'b', got {mod.original_name2}"
    assert mod.valid_game is True, "Expected valid_game=True"
    assert mod.total_len == 2, f"Expected total_len=2, got {mod.total_len}"
    assert mod.matched_chars == 0, f"Expected matched_chars=0, got {mod.matched_chars}"
    assert mod.score == 30, f"Expected score=30, got {mod.score}"
    assert mod.result == "E", f"Expected result='E', got {mod.result}"
    assert "Remaining letters: 2" in out1, "Expected 'Remaining letters: 2' in output"
    assert "Status: 😈 ENEMIES 😈" in out1, "Expected 'Status: 😈 ENEMIES 😈' in output"

    smallest_actual = {
        "score": mod.score,
        "result": mod.result,
        "relation": mod.final["rel"],
    }

    # 2. Ordinary input
    stdout_buf2 = io.StringIO()
    with patch("builtins.input", side_effect=["alex", "emma", "n"]), patch("sys.stdout", stdout_buf2):
        mod.main()
    out2 = stdout_buf2.getvalue()

    assert mod.original_name1 == "alex", f"Expected 'alex', got {mod.original_name1}"
    assert mod.original_name2 == "emma", f"Expected 'emma', got {mod.original_name2}"
    assert mod.total_len == 8, f"Expected total_len=8, got {mod.total_len}"
    assert mod.matched_chars == 4, f"Expected matched_chars=4, got {mod.matched_chars}"
    assert mod.score == 65, f"Expected score=65, got {mod.score}"
    assert mod.result == "E", f"Expected result='E', got {mod.result}"
    assert "Remaining letters: 4" in out2, "Expected 'Remaining letters: 4' in output"
    assert "Rivalry Quotient: 65%" in out2, "Expected 'Rivalry Quotient: 65%' in output"

    ordinary_actual = {
        "score": mod.score,
        "result": mod.result,
        "relation": mod.final["rel"],
    }

    return {
        "smallest_input": {
            "inputs": ["a", "b", "n"],
            "expected": {"count": 2, "score": 30, "result": "E", "relation": "Enemies"},
            "actual": smallest_actual,
            "status": "PASS",
        },
        "ordinary_input": {
            "inputs": ["alex", "emma", "n"],
            "expected": {"count": 4, "score": 65, "result": "E", "relation": "Enemies"},
            "actual": ordinary_actual,
            "status": "PASS",
        },
    }


def main():
    results = {"tool_versions": {}, "checks": []}

    # Tool versions
    py_ver = subprocess.check_output([sys.executable, "--version"], text=True).strip()
    pt_ver = subprocess.check_output([str(VENV_PYTEST), "--version"], text=True).strip()
    results["tool_versions"] = {"python": py_ver, "pytest": pt_ver}

    all_ok = True
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Check 1: Pytest test suite (test_flames_game.py)
    passed, total, rc, out = _run_pytest(ROOT / "tests" / "test_flames_game.py")
    ok1 = rc == 0 and total > 0
    results["checks"].append(
        {
            "name": "pytest_flames_game_suite",
            "command": f"{VENV_PYTEST} tests/test_flames_game.py -v --tb=short",
            "passed": passed,
            "total": total,
            "exit_code": rc,
            "status": "PASS" if ok1 else "FAIL",
        }
    )
    if not ok1:
        all_ok = False
        print(f"FAIL: pytest_flames_game_suite ({passed}/{total})")
        print(out)

    # Check 2: Direct worked example execution with mocked I/O
    try:
        example_results = _run_native_worked_example_check()
        results["checks"].append(
            {
                "name": "native_worked_example_execution",
                "command": "python native import + mocked I/O execution",
                "details": example_results,
                "status": "PASS",
            }
        )
    except Exception as exc:
        all_ok = False
        results["checks"].append(
            {
                "name": "native_worked_example_execution",
                "command": "python native import + mocked I/O execution",
                "error": str(exc),
                "status": "FAIL",
            }
        )
        print(f"FAIL: native_worked_example_execution: {exc}")

    # Check 3: Ruff lint
    target = ROOT / "games" / "FLAMES-Game" / "FLAMES-Game.py"
    test_target = ROOT / "tests" / "test_flames_game.py"
    ruff_rc = subprocess.run(
        [str(VENV_RUFF), "check", str(target), str(test_target)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    ok3 = ruff_rc.returncode == 0
    results["checks"].append(
        {
            "name": "ruff_lint",
            "command": f"{VENV_RUFF} check <source> <tests>",
            "exit_code": ruff_rc.returncode,
            "status": "PASS" if ok3 else "FAIL",
            "output": ruff_rc.stdout.strip(),
        }
    )
    if not ok3:
        all_ok = False
        print("FAIL: ruff lint")
        print(ruff_rc.stdout)

    results["timestamp"] = timestamp
    results["overall"] = "PASS" if all_ok else "FAIL"

    WORK.mkdir(parents=True, exist_ok=True)
    with open(WORK / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    with open(WORK / "report.txt", "w") as f:
        f.write(f"R26-T037 Check Report — {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        for c in results["checks"]:
            f.write(f"[{c['status']}] {c['name']}\n")
            f.write(f"       Command: {c['command']}\n")
            if "passed" in c:
                f.write(f"       Tests: {c['passed']}/{c['total']}\n")
            f.write("\n")
        f.write(f"Overall: {results['overall']}\n")

    if all_ok:
        print(f"ALL CHECKS PASSED ({results['checks'][0]['passed']} pytest tests, native execution OK, ruff clean)")
    else:
        print("SOME CHECKS FAILED — see work/R26-T037/results.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
