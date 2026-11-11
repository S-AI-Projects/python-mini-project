#!/usr/bin/env python3
"""
Focused standalone runner for R26-T006 Flipping Toss.

Validates:
- Loading fixtures from cases.json (or optional CLI path argument).
- Execution of main() in isolated state with mocked external I/O.
- Verification of independently calculated expected outputs and preconditions.
- Repeatability across consecutive executions in clean state.
- Global accuracy preservation across consecutive main() executions.
- Native project pytest test execution and non-zero test pass count.
"""

import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "games" / "Flipping-Toss" / "Flipping-Toss.py"
TEST_FILE = REPO_ROOT / "tests" / "test_flipping_toss.py"


def load_target_module(name="flipping_toss_mod"):
    spec = importlib.util.spec_from_file_location(name, TARGET_FILE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_single_fixture(module, fixture):
    inputs = list(fixture["inputs"])
    mock_random = list(fixture.get("mock_random", []))

    def mock_randint(a, b):
        if not mock_random:
            return a
        return mock_random.pop(0)

    captured_out = io.StringIO()
    with patch("builtins.input", side_effect=inputs), patch(
        "random.randint", side_effect=mock_randint
    ), patch("time.sleep"), patch("sys.stdout", new=captured_out):
        module.main()

    stdout_str = captured_out.getvalue()
    return stdout_str


def main():
    cases_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) > 1
        else Path(__file__).resolve().parent / "cases.json"
    )

    print(f"Loading cases from: {cases_path}")
    if not cases_path.is_file():
        print(f"FAIL: Cases file not found at {cases_path}")
        sys.exit(1)

    try:
        with open(cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
    except Exception as exc:
        print(f"FAIL: Could not load JSON from {cases_path}: {exc}")
        sys.exit(1)

    module = load_target_module()
    all_passed = True

    print("\n--- Running Fixture Assertions ---")
    for case in cases:
        cid = case["case_id"]
        expected_contains = case.get("expected_output_contains", [])
        expected_excludes = case.get("expected_output_excludes", [])
        expected_globals = case.get("expected_globals", {})

        try:
            stdout_str = run_single_fixture(module, case)

            for fragment in expected_contains:
                if fragment not in stdout_str:
                    raise AssertionError(
                        f"Expected fragment {fragment!r} missing from stdout."
                    )

            for fragment in expected_excludes:
                if fragment in stdout_str:
                    raise AssertionError(
                        f"Unexpected fragment {fragment!r} found in stdout."
                    )

            for var_name, expected_val in expected_globals.items():
                actual_val = getattr(module, var_name, None)
                if actual_val != expected_val:
                    raise AssertionError(
                        f"Global {var_name!r}: expected {expected_val!r}, got {actual_val!r}"
                    )

            print(f"[PASS] {cid}")
        except Exception as exc:
            all_passed = False
            print(f"[FAIL] {cid}: {exc}")

    print("\n--- Checking Repeatability (Ordinary fixture run twice in clean state) ---")
    try:
        ord_case = next(c for c in cases if c["case_id"] == "ordinary_input")
        mod_a = load_target_module("check_repeat_a")
        mod_b = load_target_module("check_repeat_b")
        out_a = run_single_fixture(mod_a, ord_case)
        out_b = run_single_fixture(mod_b, ord_case)
        if out_a != out_b:
            raise AssertionError("Consecutive runs of ordinary fixture differed.")
        print("[PASS] Repeatability verified: identical stdout across isolated runs.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Repeatability failed: {exc}")

    print("\n--- Checking Consecutive Execution Global State (accuracy preservation) ---")
    try:
        mod_seq = load_target_module("check_seq")
        ord_case = next(c for c in cases if c["case_id"] == "ordinary_input")
        small_case = next(c for c in cases if c["case_id"] == "smallest_valid_input")
        # Run 1: 1 win -> accuracy = 100.0
        run_single_fixture(mod_seq, ord_case)
        if getattr(mod_seq, "accuracy", None) != 100.0:
            raise AssertionError(f"Expected accuracy=100.0, got {getattr(mod_seq, 'accuracy', None)}")
        # Run 2: 0 tosses -> total_tosses reset to 0, accuracy preserved
        out_small = run_single_fixture(mod_seq, small_case)
        if getattr(mod_seq, "total_tosses", None) != 0:
            raise AssertionError("total_tosses was not reset to 0 in second call.")
        if getattr(mod_seq, "accuracy", None) != 100.0:
            raise AssertionError(
                f"Global accuracy was unexpectedly modified when total_tosses=0: {getattr(mod_seq, 'accuracy', None)}"
            )
        if "📈 Prediction Accuracy:" in out_small:
            raise AssertionError("Accuracy header should not be printed when total_tosses=0.")
        print("[PASS] Consecutive execution verified: total_tosses resets, accuracy preserved.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Consecutive execution check failed: {exc}")

    print("\n--- Running Native Pytest Suite ---")
    cmd = ["python3", "-m", "pytest", str(TEST_FILE), "-v"]
    cmd_str = " ".join(cmd)
    print(f"Command: {cmd_str}")

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)

    match = re.search(r"(\d+)\s+passed", proc.stdout)
    passed_count = int(match.group(1)) if match else 0
    print(f"Tests passed count: {passed_count}")

    if proc.returncode != 0 or passed_count == 0:
        all_passed = False
        print(f"[FAIL] Pytest failed or 0 tests passed (returncode={proc.returncode})")
    else:
        print(f"[PASS] Pytest passed {passed_count} test(s) cleanly.")

    if all_passed:
        print("\nALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("\nONE OR MORE CHECKS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
