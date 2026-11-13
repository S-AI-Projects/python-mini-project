"""Run the focused Progress Tracker pytest contract checks and record versions."""

import importlib.metadata
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "tests" / "test_progress_tracker.py"
RESULTS_FILE = Path(__file__).resolve().parent / "results.txt"
TEST_SUMMARY = re.compile(
    r"\b(\d+)\s+(?:passed|failed|skipped|errors?|xfailed|xpassed)\b"
)


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
    exit_code = completed.returncode
    if test_count == 0 and exit_code == 0:
        exit_code = 1

    results = (
        "Progress Tracker load_data contract checks\n"
        "Invocation: python3 work/R26-T011/check.py\n"
        f"Pytest command: {' '.join(command)}\n"
        f"Python version: {sys.version}\n"
        f"Pytest version: {pytest_version}\n"
        f"Executed test count: {test_count}\n"
        f"Pytest exit code: {completed.returncode}\n"
        f"Check exit code: {exit_code}\n"
        "\nPytest output:\n"
        f"{output}"
    )
    RESULTS_FILE.write_text(results, encoding="utf-8")
    print(output, end="")
    print(f"Executed test count: {test_count}")
    print(f"Evidence: {RESULTS_FILE}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
