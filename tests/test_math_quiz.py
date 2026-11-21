"""
Tests for games/Math-Quiz/Math-Quiz.py

Focus areas (Task R26-T031):
- Lock down the contract of play_sound(sound_type).
- Stated fixture and source data anchors:
    * Line 78:  a, b = random.randint(1, 60), random.randint(1, 60)
    * Line 127: a, b = random.randint(1, 30), random.randint(1, 30)
    * Line 575: play_sound('correct') on correct answer
    * Line 595: play_sound('wrong') on wrong answer
    * Line 605: play_sound('game_over') on terminal lives depletion
- Separate assertions for return values and observable mutation.
- Coverage for smallest supported input, ordinary input, and repeated-value domain boundary.
- External I/O (tkinter, winsound, stdout) mocked.
"""

import importlib.util
import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Math-Quiz"
    / "Math-Quiz.py"
)


def load_math_quiz_module():
    """
    Import the Math-Quiz module with external GUI dependencies mocked
    to allow headless test execution without _tkinter.
    """
    mock_tk = MagicMock()
    mock_tk._default_root = None

    with patch.dict(sys.modules, {"tkinter": mock_tk}):
        spec = importlib.util.spec_from_file_location("math_quiz", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        sys.modules["math_quiz"] = module
        spec.loader.exec_module(module)
    return module


@pytest.fixture
def math_quiz():
    return load_math_quiz_module()


# ── Return Value Contract ───────────────────────────────────────────────────

def test_play_sound_return_value_ordinary_input(math_quiz):
    """
    Ordinary input: 'correct' (referenced at line 575).
    Precondition source line: Line 575 (play_sound('correct')).
    Expected return value: None.
    """
    input_sound = "correct"
    expected = None
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound(input_sound)
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_play_sound_return_value_smallest_valid_input(math_quiz):
    """
    Smallest supported valid sound name in domain: 'wrong' (length 5, line 595).
    Precondition source line: Line 595 (play_sound('wrong')).
    Expected return value: None.
    """
    input_sound = "wrong"
    expected = None
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound(input_sound)
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_play_sound_return_value_domain_boundary_input(math_quiz):
    """
    Domain boundary input: 'game_over' (length 9, line 605).
    Precondition source line: Line 605 (play_sound('game_over')).
    Expected return value: None.
    """
    input_sound = "game_over"
    expected = None
    with patch.object(math_quiz, "winsound", MagicMock()):
        actual = math_quiz.play_sound(input_sound)
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_play_sound_return_value_unrecognized_input(math_quiz):
    """
    Unrecognized/empty input boundary: '' and 'unknown'.
    Expected return value: None.
    """
    for input_sound in ["", "unknown"]:
        with patch.object(math_quiz, "winsound", MagicMock()):
            actual = math_quiz.play_sound(input_sound)
        assert actual is None, f"Expected None for input '{input_sound}', got {actual}"


# ── Mutation Behavior Contract ──────────────────────────────────────────────

def test_play_sound_observable_mutation_isolation(math_quiz):
    """
    Verify play_sound has no observable mutation on module globals,
    function attributes, or input arguments.
    """
    module_attrs_before = set(dir(math_quiz))
    sample_input = "correct"

    with patch.object(math_quiz, "winsound", MagicMock()):
        result = math_quiz.play_sound(sample_input)

    module_attrs_after = set(dir(math_quiz))
    assert result is None
    assert module_attrs_before == module_attrs_after, "Module namespace was unexpectedly mutated"
    assert sample_input == "correct", "Input argument was mutated"


# ── Winsound Dispatch Behavior (Windows) ────────────────────────────────────

def test_play_sound_winsound_correct_beep(math_quiz):
    """
    Precondition source line: Line 32-33 (if sound_type == 'correct': winsound.Beep(1000, 150)).
    Expected action: winsound.Beep(1000, 150) called once.
    """
    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound("correct")
    mock_winsound.Beep.assert_called_once_with(1000, 150)


def test_play_sound_winsound_wrong_beep(math_quiz):
    """
    Precondition source line: Line 34-35 (elif sound_type == 'wrong': winsound.Beep(300, 300)).
    Expected action: winsound.Beep(300, 300) called once.
    """
    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound("wrong")
    mock_winsound.Beep.assert_called_once_with(300, 300)


def test_play_sound_winsound_game_over_beep(math_quiz):
    """
    Precondition source line: Line 36-37 (elif sound_type == 'game_over': winsound.Beep(200, 600)).
    Expected action: winsound.Beep(200, 600) called once.
    """
    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound("game_over")
    mock_winsound.Beep.assert_called_once_with(200, 600)


def test_play_sound_winsound_repeated_value_domain_boundary(math_quiz):
    """
    Precondition: Repeated calls with identical sound_type ('correct', 'correct').
    Expected action: winsound.Beep(1000, 150) called exactly twice in succession.
    """
    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound("correct")
        math_quiz.play_sound("correct")
    assert mock_winsound.Beep.call_count == 2
    mock_winsound.Beep.assert_called_with(1000, 150)


def test_play_sound_winsound_unrecognized_type_no_beep(math_quiz):
    """
    Precondition: An unrecognized sound_type should not trigger winsound.Beep.
    """
    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound("unsupported_sound")
    mock_winsound.Beep.assert_not_called()


def test_play_sound_winsound_exception_handling(math_quiz):
    """
    Precondition source line: Line 38-39 (except (RuntimeError, OSError): pass).
    Expected action: RuntimeError or OSError from winsound.Beep is caught without propagating.
    """
    mock_winsound = MagicMock()
    mock_winsound.Beep.side_effect = OSError("Device audio failure")
    with patch.object(math_quiz, "winsound", mock_winsound):
        # Must not raise
        result = math_quiz.play_sound("correct")
    assert result is None


# ── Non-Winsound Fallback Behavior (macOS / Linux) ──────────────────────────

def test_play_sound_fallback_tk_bell(math_quiz):
    """
    Precondition source line: Line 24-25 (if hasattr(tk, '_default_root') and tk._default_root: tk._default_root.bell()).
    Expected action: tk._default_root.bell() called once.
    """
    mock_root = MagicMock()
    mock_tk = MagicMock()
    mock_tk._default_root = mock_root

    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            math_quiz.play_sound("correct")
    mock_root.bell.assert_called_once()


def test_play_sound_fallback_stdout_bell(math_quiz):
    """
    Precondition source line: Line 27 (print('\\a', end='', flush=True)).
    Expected action: Terminal bell '\\a' output to stdout when no tk._default_root exists.
    """
    mock_tk = MagicMock()
    mock_tk._default_root = None

    captured_out = io.StringIO()
    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            with patch("sys.stdout", captured_out):
                math_quiz.play_sound("correct")

    assert captured_out.getvalue() == "\a"


def test_play_sound_fallback_exception_handling(math_quiz):
    """
    Precondition source line: Line 28-29 (except (tk.TclError, OSError) as e: print warning).
    Expected action: Handled cleanly without raising.
    """
    mock_root = MagicMock()
    mock_tk = MagicMock()
    mock_tk.TclError = RuntimeError
    mock_tk._default_root = mock_root
    mock_root.bell.side_effect = RuntimeError("TclError: display closed")

    captured_out = io.StringIO()
    with patch.object(math_quiz, "winsound", None):
        with patch.object(math_quiz, "tk", mock_tk):
            with patch("sys.stdout", captured_out):
                math_quiz.play_sound("correct")

    assert "⚠️ Warning: Sound notification failed:" in captured_out.getvalue()


# ── Source Fixture & Data Anchors Integration ───────────────────────────────

def test_fixture_anchor_line78_smallest_input(math_quiz):
    """
    Source fixture anchor: line 78:
    a, b = random.randint(1, 60), random.randint(1, 60)
    Smallest supported inputs: a = 1, b = 1 (repeated-value lower bound).
    Independently calculated sum: 1 + 1 = 2.
    Precondition line 575: correct answer triggers play_sound('correct').
    Precondition line 595: wrong answer triggers play_sound('wrong').
    """
    a, b = 1, 1
    expected_sum = 2
    assert a + b == expected_sum

    # Case 1: user provides correct answer (2) -> triggers 'correct'
    user_answer = 2
    expected_sound = "correct" if user_answer == expected_sum else "wrong"
    assert expected_sound == "correct"

    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound(expected_sound)
    mock_winsound.Beep.assert_called_once_with(1000, 150)


def test_fixture_anchor_line78_ordinary_input(math_quiz):
    """
    Source fixture anchor: line 78:
    a, b = random.randint(1, 60), random.randint(1, 60)
    Ordinary inputs: a = 15, b = 25.
    Independently calculated sum: 15 + 25 = 40.
    Wrong answer (e.g. 39) triggers play_sound('wrong') (line 595).
    """
    a, b = 15, 25
    expected_sum = 40
    assert a + b == expected_sum

    user_answer = 39
    expected_sound = "correct" if user_answer == expected_sum else "wrong"
    assert expected_sound == "wrong"

    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound(expected_sound)
    mock_winsound.Beep.assert_called_once_with(300, 300)


def test_fixture_anchor_line127_repeated_value_boundary_and_game_over(math_quiz):
    """
    Source fixture anchor: line 127:
    a, b = random.randint(1, 30), random.randint(1, 30)
    Domain boundary (repeated-value upper bound): a = 30, b = 30.
    Independently calculated sum: 30 + 30 = 60.
    Precondition line 605: wrong answer exhausting remaining lives (lives <= 0)
    triggers play_sound('game_over').
    """
    a, b = 30, 30
    expected_sum = 60
    assert a + b == expected_sum

    # Lives depleted to 0 -> triggers 'game_over' (line 605)
    lives = 1 - 1
    assert lives <= 0
    expected_sound = "game_over"

    mock_winsound = MagicMock()
    with patch.object(math_quiz, "winsound", mock_winsound):
        math_quiz.play_sound(expected_sound)
    mock_winsound.Beep.assert_called_once_with(200, 600)
