import importlib.metadata
import json
import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = ROOT / "tests" / "test_hangman_game.py"
WORK_DIR = Path(__file__).resolve().parent
CASE_RESULTS_FILE = WORK_DIR / "case-results.jsonl"
PYTEST_RESULTS_FILE = WORK_DIR / "pytest-results.xml"
RESULTS_FILE = WORK_DIR / "results.json"


def read_case_results():
    if not CASE_RESULTS_FILE.exists():
        return []
    return [
        json.loads(line)
        for line in CASE_RESULTS_FILE.read_text(encoding="utf-8").splitlines()
        if line
    ]


def read_pytest_results():
    if not PYTEST_RESULTS_FILE.exists():
        return []

    root = ElementTree.parse(PYTEST_RESULTS_FILE).getroot()
    test_cases = root.findall(".//testcase")
    results = []
    for test_case in test_cases:
        failure = test_case.find("failure")
        error = test_case.find("error")
        skipped = test_case.find("skipped")
        status = (
            "failed"
            if failure is not None
            else "error"
            if error is not None
            else "skipped"
            if skipped is not None
            else "passed"
        )
        results.append(
            {
                "name": test_case.get("name"),
                "status": status,
                "message": (
                    failure.get("message")
                    if failure is not None
                    else error.get("message")
                    if error is not None
                    else None
                ),
            }
        )
    return results


def main():
    CASE_RESULTS_FILE.write_text("", encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        f"--junitxml={PYTEST_RESULTS_FILE}",
        str(TEST_FILE),
    ]
    print(f"Command: {shlex.join(command)}", flush=True)

    environment = os.environ.copy()
    environment["HANGMAN_CHECK_EVIDENCE_FILE"] = str(CASE_RESULTS_FILE)
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    counts = [
        int(count)
        for count in re.findall(
            r"\b(\d+)\s+(?:passed|failed|error|errors|skipped|"
            r"xfailed|xpassed)\b",
            result.stdout + result.stderr,
        )
    ]
    if counts:
        print(f"Test count: {sum(counts)}")
    elif result.returncode == 0:
        print("Pytest completed without reporting a test count.", file=sys.stderr)
        result.returncode = 1

    test_results = read_pytest_results()
    report = {
        "command": shlex.join(command),
        "working_directory": str(ROOT),
        "tool_versions": {
            "python": sys.version,
            "pytest": importlib.metadata.version("pytest"),
            "platform": platform.platform(),
        },
        "test_count": len(test_results),
        "test_results": test_results,
        "case_results_file": CASE_RESULTS_FILE.name,
        "case_count": len(read_case_results()),
        "pytest_results_file": PYTEST_RESULTS_FILE.name,
        "pytest_exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    RESULTS_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Evidence: {RESULTS_FILE}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
