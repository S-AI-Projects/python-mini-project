#!/usr/bin/env python3
"""
Focused standalone runner for R26-T005 Fake News Headline Generator.

Validates:
- Loading cases from cases.json (or an optional path provided as CLI argument).
- Strict membership validation for mocked random choices.
- Execution of main() in isolated state.
- Output matching independently calculated expected results.
- Repeatability across consecutive executions.
- Input isolation across differing fixtures.
- Immutability of global collections (modes, templates).
"""

import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = (
    REPO_ROOT
    / "utilities"
    / "Fake-News-Headline-Generator"
    / "Fake-News-Headline-Generator.py"
)


def load_target_module():
    spec = importlib.util.spec_from_file_location("fake_news_gen", TARGET_FILE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fake_news_gen"] = module
    spec.loader.exec_module(module)
    return module


def make_validating_choice(expected_choices):
    it = iter(expected_choices)

    def validating_choice(seq):
        val = next(it)
        if val not in seq:
            raise AssertionError(
                f"Mocked choice {val!r} does not exist in candidate sequence {seq!r}"
            )
        return val

    return validating_choice


def run_single_case(module, case):
    mode = case["inputs"]["mode"]
    custom_subject = case["inputs"]["custom_subject"]
    custom_target = case["inputs"]["custom_target"]
    user_inputs = case["inputs"]["user_inputs"]

    all_inputs = [mode, custom_subject, custom_target] + list(user_inputs)
    val_choice = make_validating_choice(case["mock_choices"])

    captured_out = io.StringIO()
    with patch("builtins.input", side_effect=all_inputs), patch(
        "random.choice", side_effect=val_choice
    ), patch("sys.stdout", new=captured_out):
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

    # 1. Check each fixture in cases.json
    for case in cases:
        cid = case["case_id"]
        expected_headline = case["expected_headline"]
        expected_contains = case.get("expected_output_contains", [])

        try:
            stdout_str = run_single_case(module, case)

            # Check expected headline elements
            # If multi-line headline expected (e.g. boundary retry), check each line
            for hl_part in expected_headline.split("\n"):
                if hl_part not in stdout_str:
                    raise AssertionError(
                        f"Expected headline {hl_part!r} missing from stdout."
                    )

            # Check expected stdout fragments
            for fragment in expected_contains:
                if fragment not in stdout_str:
                    raise AssertionError(
                        f"Expected fragment {fragment!r} missing from stdout."
                    )

            print(f"[PASS] {cid}")
            print(f"       Expected: {expected_headline!r}")
            print("       Actual matched in stdout.")
        except Exception as exc:
            all_passed = False
            print(f"[FAIL] {cid}")
            print(f"       Expected: {expected_headline!r}")
            print(f"       Error: {exc}")

    # 2. Check Repeatability: Run Case 1 twice and assert stdout equality
    print("\nChecking Repeatability (Case 1 run twice)...")
    try:
        case_1 = cases[0]
        out_a = run_single_case(module, case_1)
        out_b = run_single_case(module, case_1)
        if out_a != out_b:
            raise AssertionError("Consecutive runs of Case 1 produced differing output.")
        print("[PASS] Repeatability verified: identical stdout across isolated runs.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Repeatability failed: {exc}")

    # 3. Check Input Isolation: Case 1 -> Case 2 -> Case 1
    print("\nChecking Input Isolation (Case 1 -> Case 2 -> Case 1)...")
    try:
        case_1 = cases[0]
        case_2 = cases[1] if len(cases) > 1 else cases[0]

        out_run1 = run_single_case(module, case_1)
        run_single_case(module, case_2)
        out_run3 = run_single_case(module, case_1)

        if out_run1 != out_run3:
            raise AssertionError(
                "Case 1 result changed after intervening execution of Case 2."
            )
        # Ensure Case 2's custom inputs did not leak into Case 1's repeat output
        custom_subj = case_2["inputs"].get("custom_subject", "")
        custom_tgt = case_2["inputs"].get("custom_target", "")
        if custom_subj and custom_subj in out_run3:
            raise AssertionError(f"Leaked custom_subject {custom_subj!r} into Case 1.")
        if custom_tgt and custom_tgt in out_run3:
            raise AssertionError(f"Leaked custom_target {custom_tgt!r} into Case 1.")

        print("[PASS] Input isolation verified: no residue from intervening call.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Input isolation failed: {exc}")

    # 4. Check Global Immutability
    print("\nChecking Global Immutability (modes and templates)...")
    try:
        modes_snap = copy.deepcopy(module.modes)
        templates_snap = copy.deepcopy(module.templates)

        # Run with custom inputs
        dummy_case = {
            "case_id": "immutability_probe",
            "inputs": {
                "mode": "general",
                "custom_subject": "IMPROBABLE_SUBJECT",
                "custom_target": "IMPROBABLE_TARGET",
                "user_inputs": ["no"],
            },
            "mock_choices": [
                "IMPROBABLE_SUBJECT",
                "launches",
                "IMPROBABLE_TARGET",
                "BREAKING NEWS: {subject} {action} {target}!",
            ],
            "expected_headline": "BREAKING NEWS: IMPROBABLE_SUBJECT launches a giant samosa!",
        }
        run_single_case(module, dummy_case)

        if module.modes != modes_snap:
            raise AssertionError("Global 'modes' was mutated during execution.")
        if module.templates != templates_snap:
            raise AssertionError("Global 'templates' was mutated during execution.")
        print("[PASS] Global immutability verified: modes and templates unchanged.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Global immutability failed: {exc}")

    if all_passed:
        print("\nALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("\nONE OR MORE CHECKS FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
