#!/usr/bin/env python3
"""
Focused runner for Task R26-T033:
GPA-Calculator: independent reference comparison [utilities/GPA-Calculator]

Responsibilities:
1. Run the native test discovery command:
   python3 -m unittest discover -s utilities/GPA-Calculator -p "test_*.py"
2. Run explicit regression checks evaluating the contract, boundaries, and reference comparison.
3. Record tool versions, nonzero test count, inputs, expected and actual results.
4. Save artifacts in work/R26-T033/results.json and work/R26-T033/report.txt.
5. Exit non-zero on failure; exit 0 on success.
"""

import importlib.util
import io
import json
import platform
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "utilities" / "GPA-Calculator" / "main.py"
OUTPUT_DIR = Path(__file__).resolve().parent


def load_module():
    spec = importlib.util.spec_from_file_location("gpa_calculator", TARGET_FILE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gpa_calculator"] = mod
    spec.loader.exec_module(mod)
    return mod


def run_checks():
    gpa_mod = load_module()
    checks = []

    def record_check(name, input_val, expected, actual, condition_met, contract_rule):
        checks.append({
            "name": name,
            "input": repr(input_val),
            "contract_rule": contract_rule,
            "expected": repr(expected),
            "actual": repr(actual),
            "status": "PASSED" if condition_met else "FAILED"
        })

    # Check 1: Stated contract: A=4 for 3 credits and B=3 for 1 credit gives 3.75
    inp_1 = [("A", 3), ("B", 1)]
    actual_1 = gpa_mod.calculate_gpa(inp_1)
    record_check(
        name="Stated contract example: A=4 for 3 credits and B=3 for 1 credit gives 3.75",
        input_val=inp_1,
        expected=3.75,
        actual=actual_1,
        condition_met=(abs(actual_1 - 3.75) < 1e-4),
        contract_rule="Goal: A=4 for 3 credits and B=3 for 1 credit gives 3.75"
    )

    # Check 2: Zero total credits rejected
    inp_2 = [("A", 0)]
    try:
        gpa_mod.calculate_gpa(inp_2)
        zero_rej = False
    except ValueError:
        zero_rej = True
    record_check(
        name="Boundary: zero total credits rejected",
        input_val=inp_2,
        expected="ValueError",
        actual="ValueError raised" if zero_rej else "No exception raised",
        condition_met=zero_rej,
        contract_rule="Goal: zero total credits rejected"
    )

    # Check 3: Unknown grades rejected
    inp_3 = [("A", 3), ("Z_INVALID", 2)]
    try:
        gpa_mod.calculate_gpa(inp_3)
        unk_rej = False
    except ValueError:
        unk_rej = True
    record_check(
        name="Boundary: unknown grades rejected",
        input_val=inp_3,
        expected="ValueError",
        actual="ValueError raised" if unk_rej else "No exception raised",
        condition_met=unk_rej,
        contract_rule="Goal: unknown grades rejected"
    )

    # Check 4: Negative credits rejected
    inp_4 = [("A", -1)]
    try:
        gpa_mod.calculate_gpa(inp_4)
        neg_rej = False
    except ValueError:
        neg_rej = True
    record_check(
        name="Boundary: negative credits rejected",
        input_val=inp_4,
        expected="ValueError",
        actual="ValueError raised" if neg_rej else "No exception raised",
        condition_met=neg_rej,
        contract_rule="Enforce positive credit constraint"
    )

    # Check 5: Custom grade-point mapping
    custom_map = {"HIGH": 5.0, "MID": 3.0}
    inp_5 = [("HIGH", 2), ("MID", 2)]
    actual_5 = gpa_mod.calculate_gpa(inp_5, grade_scale=custom_map)
    record_check(
        name="Supplied grade-point mapping support",
        input_val={"courses": inp_5, "mapping": custom_map},
        expected=4.0,
        actual=actual_5,
        condition_met=(abs(actual_5 - 4.0) < 1e-4),
        contract_rule="Goal: Calculate credit-weighted GPA from a supplied grade-point mapping"
    )

    # Check 6: Dual-method independent reference comparison
    inp_6 = [("A+", 4), ("A-", 3), ("B+", 3), ("C", 2)]
    primary_gpa = gpa_mod.calculate_gpa(inp_6)
    ref_gpa = gpa_mod.calculate_gpa_reference(inp_6)
    match_ok = (abs(primary_gpa - ref_gpa) < 1e-4)
    record_check(
        name="Focus: Dual-method independent reference comparison matches",
        input_val=inp_6,
        expected=f"primary == reference ({ref_gpa})",
        actual=f"primary={primary_gpa}, reference={ref_gpa}",
        condition_met=match_ok,
        contract_rule="Focus: Compare the result with a second simple method or an independently calculated table"
    )

    # Check 7: Reference comparison assertion failure on incorrect result
    orig_calc = gpa_mod.calculate_gpa
    try:
        gpa_mod.calculate_gpa = lambda c, s=None: 1.00  # Deliberate corruption
        try:
            gpa_mod.verify_gpa_with_reference([("A", 3), ("B", 1)])
            detected_tamper = False
        except AssertionError:
            detected_tamper = True
    finally:
        gpa_mod.calculate_gpa = orig_calc
    record_check(
        name="Focus: Assertion fails for an incorrect result",
        input_val="Tampered calculation returning incorrect 1.00",
        expected="AssertionError raised on mismatch",
        actual="AssertionError caught" if detected_tamper else "Mismatch undetected",
        condition_met=detected_tamper,
        contract_rule="Done when: The assigned contribution focus is visible and assertions fail for an incorrect result"
    )

    # Check 8: Import isolation (no side effects)
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        load_module()
    finally:
        sys.stdout = old_stdout
    no_output = (captured.getvalue() == "")
    record_check(
        name="Import isolation: no prompts, file writes, or CLI run on import",
        input_val="import utilities.GPA-Calculator.main",
        expected="No stdout output on import",
        actual="Zero stdout output" if no_output else f"Unexpected output: {captured.getvalue()}",
        condition_met=no_output,
        contract_rule="Done when: Importing the module does not prompt, write files or run the CLI"
    )

    return checks


def run_native_unittest():
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "utilities/GPA-Calculator", "-p", "test_*.py"]
    try:
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        return {
            "command": " ".join(cmd),
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "success": (proc.returncode == 0)
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


def get_git_info():
    def _git_run(args):
        try:
            return subprocess.check_output(["git"] + args, cwd=REPO_ROOT, text=True).strip()
        except Exception:
            return "unknown"
    return {
        "branch": _git_run(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": _git_run(["rev-parse", "HEAD"]),
        "status": _git_run(["status", "--short"])
    }


def main():
    print("=" * 70)
    print("🚀 Task R26-T033: GPA-Calculator Verification Runner")
    print("=" * 70)

    checks = run_checks()
    failed_checks = [c for c in checks if c["status"] != "PASSED"]

    unittest_result = run_native_unittest()

    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "platform_machine": platform.machine(),
        "git": get_git_info()
    }

    test_count = len(checks)
    all_passed = (len(failed_checks) == 0) and unittest_result["success"]

    summary_data = {
        "task_id": "R26-T033",
        "target_directory": "utilities/GPA-Calculator",
        "native_command": unittest_result["command"],
        "nonzero_test_count": test_count,
        "overall_status": "PASSED" if all_passed else "FAILED",
        "tool_versions": tool_versions,
        "checks": checks,
        "unittest_summary": {
            "command": unittest_result["command"],
            "exit_code": unittest_result["exit_code"],
            "output": unittest_result["stderr"] if unittest_result["stderr"] else unittest_result["stdout"]
        }
    }

    results_json_path = OUTPUT_DIR / "results.json"
    with open(results_json_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    report_txt_path = OUTPUT_DIR / "report.txt"
    with open(report_txt_path, "w") as f:
        f.write("Task R26-T033 Verification Report\n")
        f.write("Target: utilities/GPA-Calculator\n")
        f.write(f"Overall Status: {summary_data['overall_status']}\n")
        f.write(f"Total Checks: {test_count} (Nonzero Count Verified)\n")
        f.write(f"Native Test Command: {unittest_result['command']}\n")
        f.write(f"Unittest Exit Code: {unittest_result['exit_code']}\n\n")
        f.write("--- Tool Versions ---\n")
        f.write(f"Python: {tool_versions['python']}\n")
        f.write(f"Platform: {tool_versions['platform']} ({tool_versions['platform_machine']})\n")
        f.write(f"Git Branch: {tool_versions['git']['branch']} ({tool_versions['git']['commit'][:8]})\n\n")
        f.write("--- Contract & Reference Check Results ---\n")
        for idx, c in enumerate(checks, 1):
            f.write(f"[{idx:02d}] {c['status']}: {c['name']}\n")
            f.write(f"     Contract Rule: {c['contract_rule']}\n")
            f.write(f"     Input:    {c['input']}\n")
            f.write(f"     Expected: {c['expected']}\n")
            f.write(f"     Actual:   {c['actual']}\n\n")

    print(f"\n📊 Total Checks Executed: {test_count}")
    print(f"🛠️  Native Unittest Command: {unittest_result['command']}")
    print(f"📝 Native Unittest Result : {'PASSED' if unittest_result['success'] else 'FAILED'}")
    print(f"📁 Results Saved To       : {results_json_path}")
    print(f"📄 Report Saved To        : {report_txt_path}\n")

    for idx, c in enumerate(checks, 1):
        status_icon = "✅" if c["status"] == "PASSED" else "❌"
        print(f"{status_icon} [{idx:02d}] {c['name']}")
        print(f"    Expected: {c['expected']}")
        print(f"    Actual  : {c['actual']}")

    if not all_passed:
        print("\n❌ Verification FAILED!")
        sys.exit(1)

    print("\n✅ All GPA-Calculator contract and reference checks PASSED successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
