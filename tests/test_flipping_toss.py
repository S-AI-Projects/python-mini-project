"""
Tests for games/Flipping-Toss/Flipping-Toss.py

Validates:
- Import safety: importing does not trigger CLI execution or side effects.
- Smallest valid input fixture (quitting immediately with 0 tosses).
- Ordinary input fixture (1 round played and won, verifying 100% accuracy).
- Ordinary multi-round fixture (2 rounds played: 1 win, 1 loss, 50% accuracy).
- Boundary input handling (invalid choice and prediction retry recovery).
- Repeatability across consecutive executions in isolated state.
- Accuracy persistence behavior across consecutive main() calls (lines 5, 9-12, 60-63).
- Helper function calculate_accuracy correctness and boundary handling.
"""

import importlib.util
import io
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Flipping-Toss"
    / "Flipping-Toss.py"
)


def load_target_module(name="flipping_toss_mod"):
    """Load Flipping-Toss module fresh via importlib."""
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def target_mod():
    return load_target_module()


def test_import_safety():
    """Verify importing the module does not trigger execution or produce stdout."""
    captured = io.StringIO()
    with patch("sys.stdout", new=captured), patch("builtins.input") as mock_input:
        mod = load_target_module("safety_test_mod")
        assert hasattr(mod, "main")
        # Ensure input was never called during import
        mock_input.assert_not_called()
    assert captured.getvalue() == ""


def test_smallest_valid_fixture(target_mod):
    """
    Test smallest valid game session (0 tosses, user enters 'n' immediately).

    Precondition source lines in games/Flipping-Toss/Flipping-Toss.py:
    - Line 15: choice = input("Toss a coin? (y/n): ").lower().strip()
    - Line 49: elif choice == "n":
    - Line 60: if total_tosses > 0: (accuracy display guard)
    """
    captured = io.StringIO()
    with patch("builtins.input", side_effect=["n"]), patch(
        "time.sleep"
    ), patch("sys.stdout", new=captured):
        target_mod.main()

    out = captured.getvalue()
    assert "🪙 Coin Flip Game! 🪙" in out
    assert "👋 Thanks for playing! See you next time!" in out
    assert "📊 GAME SUMMARY 📊" in out
    assert "🪙 Total Tosses: 0" in out
    assert "👑 Heads Count: 0" in out
    assert "🦅 Tails Count: 0" in out
    assert "🎯 Correct Predictions: 0" in out
    assert "📈 Prediction Accuracy:" not in out
    assert "✨ Thanks for playing!" in out

    assert target_mod.total_tosses == 0
    assert target_mod.heads_count == 0
    assert target_mod.tails_count == 0
    assert target_mod.correct_predictions == 0


def test_ordinary_fixture_single_win(target_mod):
    """
    Test ordinary game session with 1 toss (predict 'h', flip returns Heads=1, then 'n').

    Precondition source lines in games/Flipping-Toss/Flipping-Toss.py:
    - Line 15: choice == 'y' enters toss branch; later choice == 'n' exits
    - Line 18: num = random.randint(1, 2) returns 1 (Heads)
    - Line 22: prediction = input("Predict the result (H/T): ").lower().strip()
    - Line 24: prediction in ["h", "t"] validation passes
    - Line 29: time.sleep(2) simulated toss delay
    - Line 31: total_tosses += 1
    - Lines 33-36: num == 1 sets result = "h", increments heads_count, prints Heads
    - Lines 43-45: prediction == result increments correct_predictions
    - Line 49: choice == "n" terminates game loop
    - Lines 60-63: total_tosses > 0 computes accuracy and prints percentage
    """
    captured = io.StringIO()
    with patch("builtins.input", side_effect=["y", "h", "n"]), patch(
        "random.randint", return_value=1
    ), patch("time.sleep"), patch("sys.stdout", new=captured):
        target_mod.main()

    out = captured.getvalue()
    assert "🪙 Flipping..." in out
    assert "👑 Heads!!" in out
    assert "🎉 Correct Prediction!" in out
    assert "🪙 Total Tosses: 1" in out
    assert "👑 Heads Count: 1" in out
    assert "🦅 Tails Count: 0" in out
    assert "🎯 Correct Predictions: 1" in out
    assert "📈 Prediction Accuracy: 100.00%" in out

    assert target_mod.total_tosses == 1
    assert target_mod.heads_count == 1
    assert target_mod.tails_count == 0
    assert target_mod.correct_predictions == 1
    assert target_mod.accuracy == 100.0


def test_ordinary_fixture_multi_round(target_mod):
    """
    Test ordinary multi-round session matching README sample (2 tosses: 1 win, 1 loss).

    Precondition source lines in games/Flipping-Toss/Flipping-Toss.py:
    - Line 15: choice == 'y' (rounds 1 & 2), choice == 'n' (exit)
    - Line 18: num = random.randint(1, 2) returns 1 (Heads) for both
    - Line 22: predictions 'h' (round 1) and 't' (round 2)
    - Lines 33-40: heads_count incremented to 2, tails_count remains 0
    - Lines 43-47: round 1 correct, round 2 wrong (correct_predictions = 1)
    - Lines 60-63: accuracy = (1 / 2) * 100 = 50.00%
    """
    captured = io.StringIO()
    with patch("builtins.input", side_effect=["y", "h", "y", "t", "n"]), patch(
        "random.randint", side_effect=[1, 1]
    ), patch("time.sleep"), patch("sys.stdout", new=captured):
        target_mod.main()

    out = captured.getvalue()
    assert "👑 Heads!!" in out
    assert "🎉 Correct Prediction!" in out
    assert "❌ Wrong Prediction!" in out
    assert "🪙 Total Tosses: 2" in out
    assert "👑 Heads Count: 2" in out
    assert "🦅 Tails Count: 0" in out
    assert "🎯 Correct Predictions: 1" in out
    assert "📈 Prediction Accuracy: 50.00%" in out

    assert target_mod.total_tosses == 2
    assert target_mod.heads_count == 2
    assert target_mod.tails_count == 0
    assert target_mod.correct_predictions == 1
    assert target_mod.accuracy == 50.0


def test_boundary_invalid_input_recovery(target_mod):
    """
    Test boundary input handling: invalid choice and prediction retry before success.

    Precondition source lines in games/Flipping-Toss/Flipping-Toss.py:
    - Line 15: choice == 'maybe' triggers Line 68 warning
    - Line 22: prediction == 'invalid' triggers Line 26 warning
    - Line 24: prediction == 't' breaks inner loop
    - Lines 37-40: num == 2 sets result = 't', increments tails_count
    - Lines 43-45: prediction == result increments correct_predictions
    - Lines 60-63: accuracy = (1 / 1) * 100 = 100.00%
    """
    captured = io.StringIO()
    with patch(
        "builtins.input", side_effect=["maybe", "y", "invalid", "t", "n"]
    ), patch("random.randint", return_value=2), patch("time.sleep"), patch(
        "sys.stdout", new=captured
    ):
        target_mod.main()

    out = captured.getvalue()
    assert "❌ Invalid input!! Please enter 'y' or 'n'." in out
    assert "❌ Invalid prediction!! Please enter 'H' or 'T'." in out
    assert "🦅 Tails!!" in out
    assert "🎉 Correct Prediction!" in out
    assert "🪙 Total Tosses: 1" in out
    assert "🦅 Tails Count: 1" in out
    assert "🎯 Correct Predictions: 1" in out
    assert "📈 Prediction Accuracy: 100.00%" in out


def test_repeatability_in_isolated_state():
    """Verify running the ordinary fixture twice in clean state yields identical output."""
    captured_1 = io.StringIO()
    mod_1 = load_target_module("repeat_1")
    with patch("builtins.input", side_effect=["y", "h", "n"]), patch(
        "random.randint", return_value=1
    ), patch("time.sleep"), patch("sys.stdout", new=captured_1):
        mod_1.main()

    captured_2 = io.StringIO()
    mod_2 = load_target_module("repeat_2")
    with patch("builtins.input", side_effect=["y", "h", "n"]), patch(
        "random.randint", return_value=1
    ), patch("time.sleep"), patch("sys.stdout", new=captured_2):
        mod_2.main()

    assert captured_1.getvalue() == captured_2.getvalue()


def test_accuracy_behavior_across_consecutive_main_calls(target_mod):
    """
    Verify preservation of global state behavior across consecutive main() calls.

    Lines 9-12 explicitly reset total_tosses, heads_count, tails_count, and
    correct_predictions to 0 at the start of main().
    However, accuracy is only written if total_tosses > 0 (lines 60-63).
    Therefore, if call 1 sets accuracy (e.g. 100.0) and call 2 has 0 tosses,
    total_tosses is reset to 0, but accuracy retains its prior value.
    """
    # Call 1: 1 toss, win -> sets accuracy = 100.0
    with patch("builtins.input", side_effect=["y", "h", "n"]), patch(
        "random.randint", return_value=1
    ), patch("time.sleep"), patch("sys.stdout", new=io.StringIO()):
        target_mod.main()

    assert target_mod.total_tosses == 1
    assert target_mod.accuracy == 100.0

    # Call 2: 0 tosses (quits immediately)
    captured = io.StringIO()
    with patch("builtins.input", side_effect=["n"]), patch(
        "time.sleep"
    ), patch("sys.stdout", new=captured):
        target_mod.main()

    # Counters are reset by lines 9-12
    assert target_mod.total_tosses == 0
    assert target_mod.heads_count == 0
    assert target_mod.tails_count == 0
    assert target_mod.correct_predictions == 0
    # Accuracy line is NOT printed in call 2
    assert "📈 Prediction Accuracy:" not in captured.getvalue()
    # The global variable accuracy is NOT reset by main() when total_tosses == 0
    assert target_mod.accuracy == 100.0


def test_calculate_accuracy_helper_if_present(target_mod):
    """
    Test the extracted calculate_accuracy helper once implemented.

    Guarantees baseline passes on unmodified source before refactor.
    """
    if hasattr(target_mod, "calculate_accuracy"):
        calc = target_mod.calculate_accuracy
        assert calc(0, 0) == 0.0
        assert calc(0, -1) == 0.0
        assert calc(0, 5) == 0.0
        assert calc(5, 5) == 100.0
        assert calc(1, 2) == 50.0
        assert calc(1, 3) == pytest.approx(33.333333333333336)
        assert calc(2, 3) == pytest.approx(66.66666666666667)
