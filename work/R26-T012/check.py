"""Run the focused Number Sliding Puzzle solvability boundary tests."""

import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "tests" / "test_number_sliding_puzzle.py"
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_SUMMARY = re.compile(
    r"\b(\d+)\s+(?:passed|failed|skipped|errors?|xfailed|xpassed)\b"
)
RESULT_PREFIX = "R26_T012_CASE="


def main():
    try:
        pytest_version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        print(
            "pytest is not installed for this Python interpreter; "
            "install the project's documented pytest dev dependency."
        )
        return 2

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-s",
        str(TEST_FILE),
        "-k",
        "is_solvable_contract_boundaries",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    test_count = sum(int(count) for count in TEST_SUMMARY.findall(output))
    cases = [
        json.loads(match.group(1))
        for match in re.finditer(
            re.escape(RESULT_PREFIX) + r"(\{[^\r\n]*\})",
            output,
        )
    ]

    exit_code = completed.returncode
    if test_count == 0 or len(cases) != test_count:
        exit_code = exit_code or 1

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "inputs.json").write_text(
        json.dumps(
            [
                {
                    "case": case["case"],
                    "source_anchor": case["source_anchor"],
                    "input": case["input"],
                    "expected_inversions": case["inversions"],
                    "calculation": case["calculation"],
                }
                for case in cases
            ],
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "expected.json").write_text(
        json.dumps(
            [
                {
                    "case": case["case"],
                    "expected": case["expected"],
                    "expected_calculation": case["calculation"],
                    "expected_input_after": case["input"],
                }
                for case in cases
            ],
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "actual.json").write_text(
        json.dumps(cases, indent=2) + "\n",
        encoding="utf-8",
    )

    results = (
        "Number Sliding Puzzle is_solvable boundary checks\n"
        "Invocation: python3 work/R26-T012/check.py\n"
        f"Pytest command: {' '.join(command)}\n"
        "Python version: "
        + "\n".join(line.rstrip() for line in sys.version.splitlines())
        + "\n"
        f"Pytest version: {pytest_version}\n"
        f"Executed test count: {test_count}\n"
        f"Case evidence count: {len(cases)}\n"
        f"Pytest exit code: {completed.returncode}\n"
        f"Check exit code: {exit_code}\n"
        "\nPytest output:\n"
        f"{output}"
    )
    (EVIDENCE_DIR / "results.txt").write_text(results, encoding="utf-8")
    print(output, end="")
    print(f"Executed test count: {test_count}")
    print(f"Case evidence count: {len(cases)}")
    print(f"Evidence: {EVIDENCE_DIR}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
