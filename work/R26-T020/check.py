"""Run focused _load_words contract checks and record mutation evidence."""

import importlib.metadata
import json
import platform
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_FILE = ROOT / "tests" / "test_word_building_load_words_contract.py"
CASE_PREFIX = "R26_T020_CASE="
MUTANT_PREFIX = "R26_T020_MUTANT="
SUMMARY_ITEM = re.compile(
    r"\b(\d+) (?:passed|failed|error|skipped|xfailed|xpassed)\b"
)


def main():
    command = [sys.executable, "-m", "pytest", "-q", "-s", str(TEST_FILE)]
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
        json.loads(line[line.index(CASE_PREFIX) + len(CASE_PREFIX) :])
        for line in result.stdout.splitlines()
        if CASE_PREFIX in line
    ]
    mutants = [
        json.loads(line[line.index(MUTANT_PREFIX) + len(MUTANT_PREFIX) :])
        for line in result.stdout.splitlines()
        if MUTANT_PREFIX in line
    ]
    (EVIDENCE_DIR / "results.json").write_text(
        json.dumps({"cases": cases, "mutants": mutants}, ensure_ascii=False, indent=2)
        + "\n",
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
    (EVIDENCE_DIR / "tool-versions.txt").write_text(
        f"Python: {platform.python_version()} ({sys.executable})\n"
        f"pytest: {pytest_version}\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "run-metadata.txt").write_text(
        "Automated check: python3 work/R26-T020/check.py\n"
        f"Focused pytest command: {' '.join(command)}\n"
        f"Test count: {test_count}\n"
        f"Exit status: {result.returncode}\n"
        "Mutation check: temporary _load_words comprehension filters empty "
        "buckets; original assertion must reject the mutant.\n",
        encoding="utf-8",
    )

    print(f"Command: {' '.join(command)}")
    print(f"Test count: {test_count}")
    print(f"Evidence: {EVIDENCE_DIR}")
    print(result.stdout, end="")
    if result.returncode:
        return result.returncode
    if test_count == 0:
        print("Focused pytest command did not report any tests.", file=sys.stderr)
        return 1
    if len(cases) < 2 or len(mutants) != 1:
        print("Expected fixture or mutation evidence was not produced.", file=sys.stderr)
        return 1
    if mutants[0]["mutant_actual"] == mutants[0]["expected"]:
        print("The deliberate mutant was not distinguished from expected output.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
