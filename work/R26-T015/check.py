"""Run focused deterministic checks for N-Queens print_board."""

import importlib.metadata
import json
import platform
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_FILE = ROOT / "tests" / "test_n_queens_print_board.py"
CASE_PREFIX = "R26_T015_CASE="
SUMMARY_ITEM = re.compile(
    r"\b(\d+) (?:passed|failed|error|skipped|xfailed|xpassed)\b"
)


def main():
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-s",
        str(TEST_FILE),
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (EVIDENCE_DIR / "test-output.txt").write_text(result.stdout, encoding="utf-8")

    cases = [
        json.loads(line[len(CASE_PREFIX) :])
        for line in result.stdout.splitlines()
        if line.startswith(CASE_PREFIX)
    ]
    (EVIDENCE_DIR / "results.json").write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    test_count = sum(
        int(match.group(1))
        for match in SUMMARY_ITEM.finditer(result.stdout)
    )
    try:
        pytest_version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        pytest_version = "not installed"
    tool_versions = (
        f"Python: {platform.python_version()} ({sys.executable})\n"
        f"pytest: {pytest_version}\n"
    )
    (EVIDENCE_DIR / "tool-versions.txt").write_text(
        tool_versions, encoding="utf-8"
    )

    run_metadata = (
        f"Command: {' '.join(command)}\n"
        f"Test count: {test_count}\n"
        f"Exit status: {result.returncode}\n"
    )
    (EVIDENCE_DIR / "run-metadata.txt").write_text(
        run_metadata, encoding="utf-8"
    )
    print(f"Command: {' '.join(command)}")
    print(f"Test count: {test_count}")
    print(f"Evidence: {EVIDENCE_DIR}")
    print(result.stdout, end="")
    if result.returncode:
        return result.returncode
    if test_count == 0:
        print("Focused pytest command did not report any executed tests.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
