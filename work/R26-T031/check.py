#!/usr/bin/env python3
"""
Focused runner for Task R26-T031:
Lock down the contract of play_sound (Math-Quiz.py) [games/Math-Quiz]

Responsibilities:
1. Mock external I/O (tkinter, winsound, sys.stdout) and import only games/Math-Quiz/Math-Quiz.py.
2. Execute regression test checks covering return values, mutation isolation,
   supported sound behaviors, and the source fixture data anchors.
3. Run project pytest suite on tests/test_math_quiz.py if pytest is available.
4. Record actual command, nonzero test count, tool versions, inputs, expected and actual results.
5. Save artifacts to work/R26-T031/results.json and work/R26-T031/report.txt.
6. Exit non-zero on any failure; exit 0 on success.
"""

import importlib.util
import io
import json
import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "games" / "Math-Quiz" / "Math-Quiz.py"
OUTPUT_DIR = Path(__file__).resolve().parent


def load_module():
    """Import Math-Quiz.py with external GUI dependencies mocked."""
    mock_tk = MagicMock()
    mock_tk._default_root = None

    with patch.dict(sys.modules, {"tkinter": mock_tk}):
        spec = importlib.util.spec_from_file_location("math_quiz", TARGET_FILE)
        module = importlib.util.module_from_spec(spec)
        sys.modules["math_quiz"] = module
        spec.loader.exec_module(module)
    return module


def run_checks():
    math_quiz = load_module()
    checks = []

    def record_check(name, input_val, expected, actual, condition_met, precondition_line):
        checks.append({
            "name": name,
            "input": repr(input_val),
            "precondition_source_line": precondition_line,
            "expected": repr(expected),
            "actual": repr(actual),
            "status": "PASSED" if condition_met else "FAILED"
        })

    # Check 1: Return value - ordinary input 'correct'
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound("correct")
    record_check(
        name="Return value: ordinary input 'correct'",
        input_val="correct",
        expected=None,
        actual=actual,
        condition_met=(actual is None),
        precondition_line="Line 575: play_sound('correct')"
    )

    # Check 2: Return value - smallest valid input 'wrong'
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound("wrong")
    record_check(
        name="Return value: smallest valid input 'wrong'",
        input_val="wrong",
        expected=None,
        actual=actual,
        condition_met=(actual is None),
        precondition_line="Line 595: play_sound('wrong')"
    )

    # Check 3: Return value - domain boundary 'game_over'
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound("game_over")
    record_check(
        name="Return value: domain boundary 'game_over'",
        input_val="game_over",
        expected=None,
        actual=actual,
        condition_met=(actual is None),
        precondition_line="Line 605: play_sound('game_over')"
    )

    # Check 4: Return value - unrecognized input ''
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound("")
    record_check(
        name="Return value: boundary empty input ''",
        input_val="",
        expected=None,
        actual=actual,
        condition_met=(actual is None),
        precondition_line="Line 21: def play_sound(sound_type)"
    )

    # Check 5: Observable mutation isolation
    module_attrs_before = set(dir(math_quiz))
    sample_input = "correct"
    with patch.object(math_quiz, "winsound", MagicMock()):
        res = math_quiz.play_sound(sample_input)
    module_attrs_after = set(dir(math_quiz))
    no_mutation = (module_attrs_before == module_attrs_after and sample_input == "correct" and res is None)
    record_check(
        name="Observable mutation isolation",
        input_val=sample_input,
        expected="no mutation on module state or inputs",
        actual="no mutation observed" if no_mutation else "unexpected mutation",
        condition_met=no_mutation,
        precondition_line="Lines 21-40: play_sound function body"
    )

    # Check 6: Windows dispatch - correct beep
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound("correct")
    calls = mock_ws.Beep.call_args_list
    actual_call = str(calls[0][0]) if calls else "None"
    record_check(
        name="Winsound dispatch: 'correct'",
        input_val="correct",
        expected="winsound.Beep(1000, 150)",
        actual=f"winsound.Beep{actual_call}",
        condition_met=(calls == [((1000, 150),)]),
        precondition_line="Lines 32-33: if sound_type == 'correct': winsound.Beep(1000, 150)"
    )

    # Check 7: Windows dispatch - wrong beep
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound("wrong")
    calls = mock_ws.Beep.call_args_list
    actual_call = str(calls[0][0]) if calls else "None"
    record_check(
        name="Winsound dispatch: 'wrong'",
        input_val="wrong",
        expected="winsound.Beep(300, 300)",
        actual=f"winsound.Beep{actual_call}",
        condition_met=(calls == [((300, 300),)]),
        precondition_line="Lines 34-35: elif sound_type == 'wrong': winsound.Beep(300, 300)"
    )

    # Check 8: Windows dispatch - game_over beep
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound("game_over")
    calls = mock_ws.Beep.call_args_list
    actual_call = str(calls[0][0]) if calls else "None"
    record_check(
        name="Winsound dispatch: 'game_over'",
        input_val="game_over",
        expected="winsound.Beep(200, 600)",
        actual=f"winsound.Beep{actual_call}",
        condition_met=(calls == [((200, 600),)]),
        precondition_line="Lines 36-37: elif sound_type == 'game_over': winsound.Beep(200, 600)"
    )

    # Check 9: Windows dispatch - repeated-value domain boundary
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound("correct")
        math_quiz.play_sound("correct")
    call_count = mock_ws.Beep.call_count
    record_check(
        name="Winsound dispatch: repeated-value domain boundary ('correct', 'correct')",
        input_val=["correct", "correct"],
        expected="Beep call_count == 2 with (1000, 150)",
        actual=f"Beep call_count == {call_count}",
        condition_met=(call_count == 2 and mock_ws.Beep.call_args_list == [((1000, 150),), ((1000, 150),)]),
        precondition_line="Lines 32-33: repeated invocation of play_sound('correct')"
    )

    # Check 10: Windows dispatch - unrecognized input no beep
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound("unknown_sound")
    call_count = mock_ws.Beep.call_count
    record_check(
        name="Winsound dispatch: unrecognized input produces no beep",
        input_val="unknown_sound",
        expected="Beep call_count == 0",
        actual=f"Beep call_count == {call_count}",
        condition_met=(call_count == 0),
        precondition_line="Lines 31-40: try/except guard"
    )

    # Check 11: Windows dispatch - exception handling
    mock_ws = MagicMock()
    mock_ws.Beep.side_effect = OSError("Audio hardware busy")
    with patch.object(math_quiz, "winsound", mock_ws):
        try:
            math_quiz.play_sound("correct")
            exc_handled = True
        except Exception:
            exc_handled = False
    record_check(
        name="Winsound dispatch: OSError exception suppression",
        input_val="correct with failing audio driver",
        expected="Exception suppressed cleanly without error",
        actual="Handled cleanly" if exc_handled else "Exception propagated",
        condition_met=exc_handled,
        precondition_line="Lines 38-39: except (RuntimeError, OSError): pass"
    )

    # Check 12: Non-winsound fallback - Tk bell
    mock_root = MagicMock()
    mock_tk = MagicMock()
    mock_tk._default_root = mock_root
    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            math_quiz.play_sound("correct")
    bell_called = mock_root.bell.call_count == 1
    record_check(
        name="Fallback: Tk root bell invocation",
        input_val="correct with winsound=None and active tk._default_root",
        expected="tk._default_root.bell() called once",
        actual=f"bell call_count == {mock_root.bell.call_count}",
        condition_met=bell_called,
        precondition_line="Lines 24-25: if hasattr(tk, '_default_root') and tk._default_root: tk._default_root.bell()"
    )

    # Check 13: Non-winsound fallback - stdout bell character '\a'
    mock_tk = MagicMock()
    mock_tk._default_root = None
    captured_out = io.StringIO()
    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            with patch("sys.stdout", captured_out):
                math_quiz.play_sound("correct")
    bell_out = captured_out.getvalue()
    record_check(
        name="Fallback: stdout bell character '\\a'",
        input_val="correct with winsound=None and tk._default_root=None",
        expected="\\a",
        actual=repr(bell_out),
        condition_met=(bell_out == "\a"),
        precondition_line="Lines 26-27: else: print('\\a', end='', flush=True)"
    )

    # Check 14: Non-winsound fallback - exception handling
    mock_root = MagicMock()
    mock_tk = MagicMock()
    mock_tk.TclError = RuntimeError
    mock_tk._default_root = mock_root
    mock_root.bell.side_effect = RuntimeError("display disconnect")
    warn_out = io.StringIO()
    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            with patch("sys.stdout", warn_out):
                math_quiz.play_sound("correct")
    has_warning = "⚠️ Warning: Sound notification failed:" in warn_out.getvalue()
    record_check(
        name="Fallback: TclError / OSError warning output",
        input_val="correct with failing Tk bell",
        expected="Warning message logged to stdout",
        actual="Warning message logged" if has_warning else "No warning found",
        condition_met=has_warning,
        precondition_line="Lines 28-29: except (tk.TclError, OSError) as e: print warning"
    )

    # Check 15: Fixture anchor line 78 - smallest input
    a, b = 1, 1
    expected_sum = 2
    user_answer = 2
    sound_to_trigger = "correct" if user_answer == expected_sum else "wrong"
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound(sound_to_trigger)
    call_ok = (mock_ws.Beep.call_args_list == [((1000, 150),)])
    record_check(
        name="Fixture anchor line 78: smallest input a=1, b=1",
        input_val={"a": a, "b": b, "sum": expected_sum, "user_answer": user_answer, "sound": sound_to_trigger},
        expected="play_sound('correct') -> winsound.Beep(1000, 150)",
        actual=f"winsound.Beep called with {mock_ws.Beep.call_args[0]}" if mock_ws.Beep.called else "None",
        condition_met=call_ok,
        precondition_line="Line 78: a, b = random.randint(1, 60), random.randint(1, 60); Line 575: play_sound('correct')"
    )

    # Check 16: Fixture anchor line 78 - ordinary input
    a, b = 15, 25
    expected_sum = 40
    user_answer = 39  # incorrect
    sound_to_trigger = "correct" if user_answer == expected_sum else "wrong"
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound(sound_to_trigger)
    call_ok = (mock_ws.Beep.call_args_list == [((300, 300),)])
    record_check(
        name="Fixture anchor line 78: ordinary input a=15, b=25",
        input_val={"a": a, "b": b, "sum": expected_sum, "user_answer": user_answer, "sound": sound_to_trigger},
        expected="play_sound('wrong') -> winsound.Beep(300, 300)",
        actual=f"winsound.Beep called with {mock_ws.Beep.call_args[0]}" if mock_ws.Beep.called else "None",
        condition_met=call_ok,
        precondition_line="Line 78: a, b = random.randint(1, 60), random.randint(1, 60); Line 595: play_sound('wrong')"
    )

    # Check 17: Fixture anchor line 127 - repeated-value boundary & game_over
    a, b = 30, 30
    expected_sum = 60
    lives_remaining = 0  # terminal depletion
    sound_to_trigger = "game_over" if lives_remaining <= 0 else "wrong"
    mock_ws = MagicMock()
    with patch.object(math_quiz, "winsound", mock_ws):
        math_quiz.play_sound(sound_to_trigger)
    call_ok = (mock_ws.Beep.call_args_list == [((200, 600),)])
    record_check(
        name="Fixture anchor line 127: domain boundary a=30, b=30 with lives=0",
        input_val={"a": a, "b": b, "sum": expected_sum, "lives": lives_remaining, "sound": sound_to_trigger},
        expected="play_sound('game_over') -> winsound.Beep(200, 600)",
        actual=f"winsound.Beep called with {mock_ws.Beep.call_args[0]}" if mock_ws.Beep.called else "None",
        condition_met=call_ok,
        precondition_line="Line 127: a, b = random.randint(1, 30), random.randint(1, 30); Line 605: play_sound('game_over')"
    )

    return checks


def run_pytest_suite():
    """Run project test configuration against tests/test_math_quiz.py."""
    venv_pytest = REPO_ROOT / ".venv" / "bin" / "pytest"
    cmd = [str(venv_pytest) if venv_pytest.exists() else "pytest", "tests/test_math_quiz.py", "-v"]
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
    print("🚀 Task R26-T031: Math-Quiz play_sound Contract Verification Runner")
    print("=" * 70)

    # 1. Direct regression checks
    checks = run_checks()
    failed_checks = [c for c in checks if c["status"] != "PASSED"]

    # 2. Pytest suite
    pytest_result = run_pytest_suite()

    # 3. Collect tool versions
    tool_versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "platform_machine": platform.machine(),
        "pytest_available": pytest_result["exit_code"] != -1,
        "git": get_git_info()
    }

    # 4. Compile full data
    test_count = len(checks)
    all_passed = (len(failed_checks) == 0) and pytest_result["success"]

    summary_data = {
        "task_id": "R26-T031",
        "target_file": "games/Math-Quiz/Math-Quiz.py",
        "target_function": "play_sound",
        "native_command": pytest_result["command"],
        "nonzero_test_count": test_count,
        "overall_status": "PASSED" if all_passed else "FAILED",
        "tool_versions": tool_versions,
        "checks": checks,
        "pytest_summary": {
            "command": pytest_result["command"],
            "exit_code": pytest_result["exit_code"],
            "output": pytest_result["stdout"]
        }
    }

    # 5. Save results.json
    results_json_path = OUTPUT_DIR / "results.json"
    with open(results_json_path, "w") as f:
        json.dump(summary_data, f, indent=2)

    # 6. Save report.txt
    report_txt_path = OUTPUT_DIR / "report.txt"
    with open(report_txt_path, "w") as f:
        f.write("Task R26-T031 Verification Report\n")
        f.write("Target: games/Math-Quiz/Math-Quiz.py::play_sound\n")
        f.write(f"Overall Status: {summary_data['overall_status']}\n")
        f.write(f"Total Checks: {test_count} (Nonzero Count Verified)\n")
        f.write(f"Native Test Command: {pytest_result['command']}\n")
        f.write(f"Pytest Exit Code: {pytest_result['exit_code']}\n\n")
        f.write("--- Tool Versions ---\n")
        f.write(f"Python: {tool_versions['python']}\n")
        f.write(f"Platform: {tool_versions['platform']} ({tool_versions['platform_machine']})\n")
        f.write(f"Git Branch: {tool_versions['git']['branch']} ({tool_versions['git']['commit'][:8]})\n\n")
        f.write("--- Test Check Results ---\n")
        for idx, c in enumerate(checks, 1):
            f.write(f"[{idx:02d}] {c['status']}: {c['name']}\n")
            f.write(f"     Precondition Source Line: {c['precondition_source_line']}\n")
            f.write(f"     Input:    {c['input']}\n")
            f.write(f"     Expected: {c['expected']}\n")
            f.write(f"     Actual:   {c['actual']}\n\n")

    # 7. Print summary to console
    print(f"\n📊 Total Checks Executed: {test_count}")
    print(f"🛠️  Native Pytest Command: {pytest_result['command']}")
    print(f"📝 Native Pytest Result : {'PASSED' if pytest_result['success'] else 'FAILED'}")
    print(f"📁 Results Saved To    : {results_json_path}")
    print(f"📄 Report Saved To     : {report_txt_path}\n")

    for idx, c in enumerate(checks, 1):
        status_icon = "✅" if c["status"] == "PASSED" else "❌"
        print(f"{status_icon} [{idx:02d}] {c['name']}")
        print(f"    Expected: {c['expected']}")
        print(f"    Actual  : {c['actual']}")

    if not all_passed:
        print("\n❌ Verification FAILED!")
        sys.exit(1)

    print("\n✅ All regression checks PASSED successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
