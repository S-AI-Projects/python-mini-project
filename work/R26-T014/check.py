"""Run deterministic Dots & Boxes helper checks and a mutation sensitivity check."""

import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "games" / "Dots-Boxes-AI" / "Dots-Boxes-AI.py"
TEST_FILE = ROOT / "tests" / "test_dots_boxes_ai.py"
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_SUMMARY = re.compile(
    r"\b(\d+)\s+(?:passed|failed|skipped|errors?|xfailed|xpassed)\b"
)
RESULT_PREFIX = "R26_T014_CASE="
EXPECTED_CASES = 130


def _run(command, env=None):
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _clean_output(output):
    return "\n".join(line.rstrip() for line in output.splitlines()).rstrip() + "\n"


def _write_json_records(path, records):
    encoded = (
        json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        for record in records
    )
    path.write_text("[\n" + ",\n".join(encoded) + "\n]\n", encoding="utf-8")


def main():
    try:
        pytest_version = importlib.metadata.version("pytest")
    except importlib.metadata.PackageNotFoundError:
        print(
            "pytest is not installed for this Python interpreter; "
            "install the project's documented pytest dev dependency."
        )
        return 2

    command = [sys.executable, "-m", "pytest", "-q", "-s", str(TEST_FILE)]
    completed = _run(command)
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

    mutant_command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        str(TEST_FILE),
        "-k",
        "smallest",
    ]
    with tempfile.TemporaryDirectory(prefix="r26-t014-mutant-") as temp_dir:
        mutant_source = Path(temp_dir) / SOURCE.name
        original_source = SOURCE.read_text(encoding="utf-8")
        mutation_target = "    return affected\n"
        if original_source.count(mutation_target) != 1:
            print("Unable to apply temporary mutation: return site not unique.")
            return 2
        mutant_source.write_text(
            original_source.replace(mutation_target, "    return []\n", 1),
            encoding="utf-8",
        )
        mutant_env = dict(os.environ)
        mutant_env["DOTS_BOXES_SOURCE"] = str(mutant_source)
        mutant = _run(mutant_command, env=mutant_env)
        mutant_output = _clean_output(mutant.stdout + mutant.stderr).rstrip()

    mutant_detected = mutant.returncode != 0
    failure_is_minimal = "smallest horizontal top edge" in mutant_output
    exit_code = completed.returncode
    if test_count == 0 or len(cases) != EXPECTED_CASES:
        exit_code = exit_code or 1
    if not mutant_detected or not failure_is_minimal:
        exit_code = exit_code or 1

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    _write_json_records(
        EVIDENCE_DIR / "inputs.json",
        [
            {
                "case": case["case"],
                "source_anchor": case["source_anchor"],
                "input": case["input"],
            }
            for case in cases
        ],
    )
    _write_json_records(
        EVIDENCE_DIR / "expected.json",
        [
            {
                "case": case["case"],
                "expected": case["expected"],
                "reference": case.get("reference"),
            }
            for case in cases
        ],
    )
    _write_json_records(EVIDENCE_DIR / "actual.json", cases)

    failure_signature = [
        line.strip()
        for line in mutant_output.splitlines()
        if line.startswith("_ test_small_valid_inputs")
        or "AssertionError:" in line
        or "expected [(0, 0)], got []" in line
        or line.startswith("FAILED ")
        or line.startswith("1 failed")
    ]
    mutant_evidence = (
        "Deliberately changed the helper's return to `return []` in a temporary "
        "source copy.\n"
        f"Command: {' '.join(mutant_command)}\n"
        f"Exit code: {mutant.returncode}\n"
        f"Detected by tests: {mutant_detected}\n"
        f"Smallest case failed: {failure_is_minimal}\n"
        "Minimal failure signature:\n"
        + "\n".join(failure_signature)
        + "\n"
    )
    (EVIDENCE_DIR / "mutation.txt").write_text(
        mutant_evidence.rstrip() + "\n",
        encoding="utf-8",
    )

    results = (
        "Dots & Boxes get_affected_boxes invariant checks\n"
        "Invocation: python3 work/R26-T014/check.py\n"
        f"Pytest command: {' '.join(command)}\n"
        "Python version: "
        + "\n".join(line.rstrip() for line in sys.version.splitlines())
        + "\n"
        f"Pytest version: {pytest_version}\n"
        f"Executed test count: {test_count}\n"
        f"Recorded valid cases: {len(cases)}\n"
        f"Mutant detected: {mutant_detected}\n"
        f"Minimal case detected: {failure_is_minimal}\n"
        f"Pytest exit code: {completed.returncode}\n"
        f"Check exit code: {exit_code}\n"
        "\nPytest output:\n"
        f"{_clean_output(summary_output if completed.returncode == 0 else output)}\n"
        "\nMutation check:\n"
        f"{mutant_evidence}"
    )
    (EVIDENCE_DIR / "results.txt").write_text(
        results.rstrip() + "\n",
        encoding="utf-8",
    )
    print(summary_output or output, end="\n")
    print(mutant_evidence)
    print(f"Evidence: {EVIDENCE_DIR}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
