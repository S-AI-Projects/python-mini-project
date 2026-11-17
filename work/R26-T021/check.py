"""Run the focused Complete Calculus Engine regression tests."""

import builtins
import importlib.util
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
TEST_MODULE = ROOT / "tests" / "test_complete_calculus_engine.py"
SOURCE_MODULE = ROOT / "math" / "Complete-Calculus-Engine" / "Complete-Calculus-Engine.py"
RESULTS_FILE = Path(__file__).resolve().parent / "results.json"
CASES = [
    {
        "input": "3x^2 - x^-1 + 5",
        "expected": [
            {"coeff": 3.0, "power": 2, "is_ln": False},
            {"coeff": 5.0, "power": 0, "is_ln": False},
            {"coeff": -1.0, "power": -1, "is_ln": False},
        ],
    },
    {
        "input": "2x + 3 - x",
        "expected": [
            {"coeff": 1.0, "power": 1, "is_ln": False},
            {"coeff": 3.0, "power": 0, "is_ln": False},
        ],
    },
    {"input": "", "expected": None},
    {"input": "x + 2y", "expected": None},
    {"input": "x +", "expected": None},
    {"input": "2**x", "expected": None},
]


def collect_actual_results():
    spec = importlib.util.spec_from_file_location("complete_calculus_engine", SOURCE_MODULE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load parser module from {SOURCE_MODULE}")

    module = importlib.util.module_from_spec(spec)
    with patch.object(builtins, "input", return_value=""), patch.object(
        builtins, "print"
    ):
        spec.loader.exec_module(module)

    return [
        {**case, "actual": module.parse_polynomial(case["input"])}
        for case in CASES
    ]


def main():
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        str(ROOT / "pyproject.toml"),
        "-q",
        str(TEST_MODULE),
    ]
    display_command = shlex.join(command)
    print(f"Running focused checks: {display_command}", flush=True)
    completed = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    print(completed.stdout, end="")
    print(completed.stderr, end="", file=sys.stderr)

    actual_results = collect_actual_results()
    outcome_counts = {
        outcome: sum(
            int(count)
            for count, name in re.findall(
                r"\b(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed)\b",
                completed.stdout + completed.stderr,
            )
            if name == outcome or (outcome == "errors" and name == "error")
        )
        for outcome in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")
    }
    test_count = sum(outcome_counts.values())
    report = {
        "invocation": "python3 work/R26-T021/check.py",
        "command": display_command,
        "python_version": sys.version,
        "pytest_version": __import__("pytest").__version__,
        "test_count": test_count,
        "outcome_counts": outcome_counts,
        "exit_code": completed.returncode,
        "output": completed.stdout + completed.stderr,
        "cases": actual_results,
    }
    RESULTS_FILE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Saved check results to {RESULTS_FILE}")

    if test_count == 0:
        print("Focused test runner reported no test outcomes.", file=sys.stderr)
        return completed.returncode or 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
