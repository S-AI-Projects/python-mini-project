"""Run focused Reverse Hangman reversal-reference tests and save evidence."""

import importlib.metadata
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "tests" / "test_reverse_hangman_game.py"
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_SUMMARY = re.compile(
    r"\b(\d+)\s+(?:passed|failed|skipped|errors?|xfailed|xpassed)\b"
)
RESULT_PREFIX = "R26_T013_CASE="


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
    summary_output = "\n".join(
        line for line in output.splitlines() if TEST_SUMMARY.search(line)
    )
    cases = [
        json.loads(match.group(1))
        for match in re.finditer(
            re.escape(RESULT_PREFIX) + r"(\{[^\r\n]*\})",
            output,
        )
    ]
    exit_code = completed.returncode
    if test_count == 0 or len(cases) != test_count - 1:
        exit_code = exit_code or 1

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "inputs.json").write_text(
        json.dumps(
            [
                {
                    "case": case["case"],
                    "input": case["input"],
                    "expected_length": case["expected_length"],
                }
                for case in cases
            ],
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "expected.json").write_text(
        json.dumps(
            [
                {
                    "case": case["case"],
                    "expected": case["expected"],
                    "reference": case["reference"],
                    "expected_twice": case["expected_twice"],
                    "expected_length": case["expected_length"],
                }
                for case in cases
            ],
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "actual.json").write_text(
        json.dumps(cases, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    results = (
        "Reverse Hangman sequence reversal reference checks\n"
        "Invocation: python3 work/R26-T013/check.py\n"
        f"Pytest command: {' '.join(command)}\n"
        "Python version: "
        + "\n".join(line.rstrip() for line in sys.version.splitlines())
        + "\n"
        f"Pytest version: {pytest_version}\n"
        f"Executed test count: {test_count}\n"
        f"Input cases recorded: {len(cases)}\n"
        f"Pytest exit code: {completed.returncode}\n"
        f"Check exit code: {exit_code}\n"
        "\nPytest output:\n"
        f"{summary_output if completed.returncode == 0 else output}\n"
    )
    (EVIDENCE_DIR / "results.txt").write_text(results, encoding="utf-8")
    print(summary_output or output, end="\n")
    print(f"Executed test count: {test_count}")
    print(f"Input cases recorded: {len(cases)}")
    print(f"Evidence: {EVIDENCE_DIR}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
