"""Run focused Tic-Tac-Toe correctness/scaling checks and save evidence."""

import importlib.metadata
import json
import os
import platform
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = Path(__file__).resolve().parent
TEST_FILE = ROOT / "tests" / "test_tic_tac_toe_scaling.py"
BENCHMARK_PREFIX = "R26_T019_BENCHMARK="
SUMMARY_ITEM = re.compile(
    r"\b(\d+) (?:passed|failed|error|skipped|xfailed|xpassed)\b"
)


def main():
    command = [sys.executable, "-m", "pytest", "-q", "-s", str(TEST_FILE)]
    environment = {
        **os.environ,
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",
    }
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (EVIDENCE_DIR / "test-output.txt").write_text(result.stdout, encoding="utf-8")
    benchmark_line = next(
        (
            line[len(BENCHMARK_PREFIX) :]
            for line in result.stdout.splitlines()
            if line.startswith(BENCHMARK_PREFIX)
        ),
        None,
    )
    if benchmark_line is None:
        benchmark_data = []
    else:
        benchmark_data = json.loads(benchmark_line)
    (EVIDENCE_DIR / "results.json").write_text(
        json.dumps(benchmark_data, ensure_ascii=False, indent=2) + "\n",
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
    try:
        pygame_version = importlib.metadata.version("pygame")
    except importlib.metadata.PackageNotFoundError:
        pygame_version = "not installed"
    (EVIDENCE_DIR / "tool-versions.txt").write_text(
        f"Python: {platform.python_version()} ({sys.executable})\n"
        f"pytest: {pytest_version}\n"
        f"pygame: {pygame_version}\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "run-metadata.txt").write_text(
        "Automated check: python3 work/R26-T019/check.py\n"
        f"Focused pytest command: {' '.join(command)}\n"
        "SDL video/audio drivers: dummy\n"
        "Test count: " + str(test_count) + "\n"
        f"Exit status: {result.returncode}\n"
        "Performance methodology: 5 operation-count runs and 5 wall-time "
        "runs per input size (1, 3, 5 clicks); main timings exclude process "
        "startup, import, and compilation, include pygame init and dummy "
        "rendering; deterministic inputs use no randomness; no pass/fail "
        "timing threshold.\n",
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
    if not benchmark_data:
        print("No benchmark results were captured.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
