"""
Regression tests for `clear` in games/Word-Scramble-Game/Word-Scramble-Game.py

Task  : R26-T051  (GitHub issue #6)
Author: Rhea Sharma
Date  : 2026-11-18

Design notes
------------
* The file name contains hyphens so it cannot be imported with a normal
  `import` statement.  We use importlib.util.spec_from_file_location as done
  in other tests in this test suite (e.g. test_emoji_memory_game.py).
* All calls to os.system are mocked so the test suite never touches the
  terminal or any external resource (Rule 6 – mock all external I/O).
* Independently calculated expected values are stated as literals in each
  test before the call under test is made.
* Each test names the source file line that establishes the precondition
  being checked.

Fixture anchors from the source (mentioned in issue #6):
  note = []        – line 280 of Word-Scramble-Game.py (pre-edit line 276)
  valid_words = [] – line 349 of Word-Scramble-Game.py (pre-edit line 345)
These confirm the game state that calls clear() with no prior mutation.
"""

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import call, patch

import pytest

# ---------------------------------------------------------------------------
# Module loading – hyphened filename requires importlib, not plain import
# ---------------------------------------------------------------------------
_MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Word-Scramble-Game"
    / "Word-Scramble-Game.py"
)


def _load_wsg():
    """Load Word-Scramble-Game as a fresh module object each time."""
    spec = importlib.util.spec_from_file_location("word_scramble_game", _MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Register under a consistent key so repeated loads share one entry
    sys.modules["word_scramble_game"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def wsg():
    """Return the Word-Scramble-Game module (loaded once per test session)."""
    return _load_wsg()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _expected_cmd():
    """
    Independently calculate the expected os.system argument for this platform.
    Source precondition: line 87 – ``os.system("cls" if os.name == "nt" else "clear")``
    """
    return "cls" if os.name == "nt" else "clear"


# ===========================================================================
# Test class
# ===========================================================================

class TestClear:
    """
    Focused regression tests for the ``clear`` helper function.

    clear() contract (source line 82-87):
      Input  : none
      Returns: None   (os.system return value is discarded)
      Effect : runs "cls" on Windows (os.name == "nt") or
               "clear" on POSIX (os.name == "posix") via os.system.
    """

    # -----------------------------------------------------------------------
    # T1 – Smallest valid input: single call, return value is None
    # -----------------------------------------------------------------------
    def test_clear_smallest_input_returns_none(self, wsg):
        """
        Precondition (source line 82): ``def clear():`` – the function
        accepts zero arguments; a single bare call is the smallest valid use.

        Fixture anchor (source line 280): ``note = []`` – at the point where
        clear() is first called after a correct answer, no note items have
        been accumulated yet, mirroring the smallest/no-side-effect state.

        Expected (independently calculated):
          clear() does NOT return the os.system exit code; the function body
          contains no ``return`` statement, so the return value is always None.
        """
        expected_return = None                 # independent calculation

        with patch("os.system") as mock_sys:
            mock_sys.return_value = 0          # simulate successful clear
            actual_return = wsg.clear()

        # Assert the returned value – not just successful execution
        assert actual_return == expected_return, (
            f"Expected clear() to return {expected_return!r}, "
            f"got {actual_return!r}"
        )

    # -----------------------------------------------------------------------
    # T2 – Smallest valid input: correct OS command is dispatched
    # -----------------------------------------------------------------------
    def test_clear_smallest_input_calls_correct_command(self, wsg):
        """
        Precondition (source line 87):
          ``os.system("cls" if os.name == "nt" else "clear")``
          The command is chosen at call time by inspecting os.name.

        Fixture anchor (source line 349): ``valid_words = []`` – the game
        resets this list at the top of every round loop before calling clear(),
        confirming there is no accumulated game state that could alter the
        command.

        Expected (independently calculated):
          On this platform os.name == {os.name!r}, so the expected command is
          {"cls" if os.name == "nt" else "clear"!r}.
        """
        expected_cmd = _expected_cmd()         # independent calculation

        with patch("os.system") as mock_sys:
            wsg.clear()
            actual_calls = mock_sys.call_args_list

        # Assert mutation: exactly one call with the right argument
        assert len(actual_calls) == 1, (
            f"Expected os.system called 1 time, got {len(actual_calls)}"
        )
        actual_cmd = actual_calls[0].args[0]
        assert actual_cmd == expected_cmd, (
            f"Expected os.system({expected_cmd!r}), got os.system({actual_cmd!r})"
        )

    # -----------------------------------------------------------------------
    # T3 – Ordinary input: a typical in-game call (after a correct guess)
    # -----------------------------------------------------------------------
    def test_clear_ordinary_call_dispatches_once(self, wsg):
        """
        Precondition (source line 278):
          ``clear()`` is called immediately after a correct word guess, before
          the score header is reprinted.  This is the ordinary game usage.

        Expected (independently calculated):
          os.system is invoked exactly once per call to clear().
          The return value from clear() is None.
        """
        expected_call_count = 1                # independent calculation
        expected_return     = None             # independent calculation
        expected_cmd        = _expected_cmd()  # independent calculation

        with patch("os.system") as mock_sys:
            mock_sys.return_value = 0
            actual_return = wsg.clear()
            actual_call_count = mock_sys.call_count
            actual_cmd = mock_sys.call_args[0][0]

        assert actual_call_count == expected_call_count, (
            f"Expected {expected_call_count} os.system call(s), "
            f"got {actual_call_count}"
        )
        assert actual_cmd == expected_cmd, (
            f"Expected os.system({expected_cmd!r}), got os.system({actual_cmd!r})"
        )
        assert actual_return == expected_return, (
            f"Expected return value {expected_return!r}, got {actual_return!r}"
        )

    # -----------------------------------------------------------------------
    # T4 – Repeated-value / boundary: calling clear() multiple times
    # -----------------------------------------------------------------------
    def test_clear_repeated_calls_each_dispatch_once(self, wsg):
        """
        Precondition (source lines 278, 295, 316):
          clear() is called multiple times per game session (after correct
          answer, after running out of attempts, in game-over screen).
          Each call must independently dispatch os.system once.

        Expected (independently calculated):
          Calling clear() N times → os.system called exactly N times, each
          with the same platform-appropriate command.  No state leaks between
          calls.
        """
        n_calls      = 3                           # repeated-value boundary
        expected_cmd = _expected_cmd()             # independent calculation
        expected_total_calls = n_calls             # 1 per clear() invocation
        expected_per_call    = [call(expected_cmd)] * n_calls

        with patch("os.system") as mock_sys:
            mock_sys.return_value = 0
            for _ in range(n_calls):
                wsg.clear()

            actual_total_calls = mock_sys.call_count
            actual_per_call    = mock_sys.call_args_list

        assert actual_total_calls == expected_total_calls, (
            f"Expected {expected_total_calls} total os.system calls across "
            f"{n_calls} clear() invocations, got {actual_total_calls}"
        )
        assert actual_per_call == expected_per_call, (
            f"Expected each call = os.system({expected_cmd!r}), "
            f"got {actual_per_call!r}"
        )

    # -----------------------------------------------------------------------
    # T5 – Boundary: os.system failure (non-zero exit) does not change return
    # -----------------------------------------------------------------------
    def test_clear_returns_none_even_when_os_system_fails(self, wsg):
        """
        Precondition (source line 87):
          clear() does not check or propagate the os.system exit code.
          Even if the underlying command fails (exit 1), the function must
          still return None, preserving the existing public interface.

        Expected (independently calculated):
          Return value is always None regardless of os.system's exit code.
          This is the boundary case where os.system signals failure.
        """
        expected_return = None                 # independent calculation

        with patch("os.system") as mock_sys:
            mock_sys.return_value = 1          # simulate failed clear
            actual_return = wsg.clear()

        assert actual_return == expected_return, (
            f"Expected clear() to return {expected_return!r} even when "
            f"os.system returns a non-zero exit code, got {actual_return!r}"
        )
