"""Tests for main() in games/FLAMES-Game/FLAMES-Game.py (R26-T037).

Written BEFORE updating the implementation documentation.
Every assertion has an explicit expected value calculated independently.
Preconditions reference exact source lines from games/FLAMES-Game/FLAMES-Game.py.

Source fixture/data anchors:
- Line 5:  session = {"rounds": 0,"results": {r: 0 for r in "FLAMES"},"total_score": 0,}
- Line 80: flames = ['F', 'L', 'A', 'M', 'E', 'S']
"""

import importlib.util
import io
from pathlib import Path
from unittest.mock import patch

import pytest

_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "FLAMES-Game"
    / "FLAMES-Game.py"
)


def _load_module():
    """Load the FLAMES-Game module dynamically (file name contains a hyphen)."""
    spec = importlib.util.spec_from_file_location("flames_game", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def flames_mod():
    """Provide a fresh instance of the FLAMES-Game module for each test."""
    return _load_module()


# ============================================================================
# Smallest Valid Input: name1="a", name2="b", choice="n"
# ============================================================================
class TestSmallestValidInput:
    """Smallest valid input: two 1-letter names with no common characters.

    Preconditions:
    - Line 5:  session initialized: {"rounds": 0, "results": {r: 0 for r in "FLAMES"}, "total_score": 0}
    - Line 34: name1 input read, stripped, lowercased: 'a' (line 35: 'a'.isalpha() is True)
    - Line 41: name2 input read, stripped, lowercased: 'b' (line 42: 'b'.isalpha() is True)
    - Line 49: name1_list = ['a']
    - Line 50: name2_list = ['b']
    - Line 52: Cancellation loop: 'a' not in ['b'], no characters removed
    - Line 57: count = len(['a']) + len(['b']) = 2
    - Line 60: valid_game = True (count 2 != 0)
    - Line 73: total_len = len('a') + len('b') = 2
    - Line 74: matched_chars = 2 - 2 = 0
    - Line 75: score = 30 + round((0 / 2) * 70) = 30
    - Line 80: flames = ['F', 'L', 'A', 'M', 'E', 'S'] (anchor)
    - Lines 81-84: Cyclic elimination loop with count=2:
        Round 1: index = (0 + 2 - 1) % 6 = 1 -> 'L' popped -> ['F', 'A', 'M', 'E', 'S']
        Round 2: index = (1 + 2 - 1) % 5 = 2 -> 'M' popped -> ['F', 'A', 'E', 'S']
        Round 3: index = (2 + 2 - 1) % 4 = 3 -> 'S' popped -> ['F', 'A', 'E']
        Round 4: index = (3 + 2 - 1) % 3 = 1 -> 'A' popped -> ['F', 'E']
        Round 5: index = (1 + 2 - 1) % 2 = 0 -> 'F' popped -> ['E']
    - Line 86: result = flames[0] = 'E'
    - Line 87: final = mapping['E'] = {"rel": "Enemies", "emoji": "😈", "metric": "Rivalry Quotient"}
    - Lines 90-92: session updated: rounds=1, results['E']=1, total_score=30
    - Line 113: choice = 'n' terminates the game loop
    """

    def test_smallest_valid_input_state_and_output(self, flames_mod):
        inputs = ["a", "b", "n"]
        stdout_buf = io.StringIO()

        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", stdout_buf):
            flames_mod.main()

        output = stdout_buf.getvalue()

        # Assert module-level global variables established by main()
        assert flames_mod.original_name1 == "a"
        assert flames_mod.original_name2 == "b"
        assert flames_mod.valid_game is True
        assert flames_mod.total_len == 2
        assert flames_mod.matched_chars == 0
        assert flames_mod.score == 30
        assert flames_mod.result == "E"
        assert flames_mod.final == {
            "rel": "Enemies",
            "emoji": "😈",
            "metric": "Rivalry Quotient",
        }

        # Assert expected text displayed in stdout (including remaining letters count)
        assert "Remaining letters: 2" in output
        assert "Names: A & B" in output
        assert "Status: 😈 ENEMIES 😈" in output
        assert "Rivalry Quotient: 30%" in output
        assert "Result: Enemies 😈" in output
        assert "Total Rounds Played : 1" in output
        assert "Enemies     :  1  █" in output
        assert "Most Common Result  : Enemies 😈" in output
        assert "Avg Score           : 30.0%" in output
        assert "Thanks for playing FLAMES! Goodbye!" in output


# ============================================================================
# Ordinary Input: name1="alex", name2="emma", choice="n"
# ============================================================================
class TestOrdinaryInput:
    """Ordinary input: multi-character names with partial letter overlap.

    Preconditions:
    - Line 5:  session initialized: {"rounds": 0, "results": {r: 0 for r in "FLAMES"}, "total_score": 0}
    - Line 34: name1 input = 'alex' (line 35: 'alex'.isalpha() is True)
    - Line 41: name2 input = 'emma' (line 42: 'emma'.isalpha() is True)
    - Line 49: name1_list = ['a', 'l', 'e', 'x']
    - Line 50: name2_list = ['e', 'm', 'm', 'a']
    - Line 52: Cancellation:
        'a' in name2_list -> removed from both -> name1: ['l', 'e', 'x'], name2: ['e', 'm', 'm']
        'e' in name2_list -> removed from both -> name1: ['l', 'x'], name2: ['m', 'm']
        'l', 'x' not in name2_list
        Remaining: name1_list = ['l', 'x'], name2_list = ['m', 'm']
    - Line 57: count = len(['l', 'x']) + len(['m', 'm']) = 2 + 2 = 4
    - Line 60: valid_game = True (count 4 != 0)
    - Line 73: total_len = len('alex') + len('emma') = 8
    - Line 74: matched_chars = 8 - 4 = 4
    - Line 75: score = 30 + round((4 / 8) * 70) = 30 + round(35.0) = 65
    - Line 80: flames = ['F', 'L', 'A', 'M', 'E', 'S'] (anchor)
    - Lines 81-84: Cyclic elimination loop with count=4:
        Round 1: index = (0 + 4 - 1) % 6 = 3 -> 'M' popped -> ['F', 'L', 'A', 'E', 'S']
        Round 2: index = (3 + 4 - 1) % 5 = 1 -> 'L' popped -> ['F', 'A', 'E', 'S']
        Round 3: index = (1 + 4 - 1) % 4 = 0 -> 'F' popped -> ['A', 'E', 'S']
        Round 4: index = (0 + 4 - 1) % 3 = 0 -> 'A' popped -> ['E', 'S']
        Round 5: index = (0 + 4 - 1) % 2 = 1 -> 'S' popped -> ['E']
    - Line 86: result = flames[0] = 'E'
    - Line 87: final = mapping['E'] = {"rel": "Enemies", "emoji": "😈", "metric": "Rivalry Quotient"}
    - Lines 90-92: session updated: rounds=1, results['E']=1, total_score=65
    - Line 113: choice = 'n' terminates the game loop
    """

    def test_ordinary_input_state_and_output(self, flames_mod):
        inputs = ["alex", "emma", "n"]
        stdout_buf = io.StringIO()

        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", stdout_buf):
            flames_mod.main()

        output = stdout_buf.getvalue()

        assert flames_mod.original_name1 == "alex"
        assert flames_mod.original_name2 == "emma"
        assert flames_mod.valid_game is True
        assert flames_mod.total_len == 8
        assert flames_mod.matched_chars == 4
        assert flames_mod.score == 65
        assert flames_mod.result == "E"
        assert flames_mod.final == {
            "rel": "Enemies",
            "emoji": "😈",
            "metric": "Rivalry Quotient",
        }

        assert "Remaining letters: 4" in output
        assert "Names: Alex & Emma" in output
        assert "Status: 😈 ENEMIES 😈" in output
        assert "Rivalry Quotient: 65%" in output
        assert "Result: Enemies 😈" in output
        assert "Total Rounds Played : 1" in output
        assert "Avg Score           : 65.0%" in output


# ============================================================================
# Second Ordinary Input: name1="john", name2="mary", choice="n" (Result: 'A')
# ============================================================================
class TestSecondOrdinaryInput:
    """Second ordinary input yielding a different relation: 'A' (Affection).

    Preconditions:
    - Line 57: count = 8 ('john' and 'mary' share 0 letters)
    - Line 75: score = 30 + round((0 / 8) * 70) = 30
    - Lines 81-84: Cyclic elimination loop with count=8:
        Round 1: index = (0 + 7) % 6 = 1 -> 'L' popped -> ['F', 'A', 'M', 'E', 'S']
        Round 2: index = (1 + 7) % 5 = 3 -> 'E' popped -> ['F', 'A', 'M', 'S']
        Round 3: index = (3 + 7) % 4 = 2 -> 'M' popped -> ['F', 'A', 'S']
        Round 4: index = (2 + 7) % 3 = 0 -> 'F' popped -> ['A', 'S']
        Round 5: index = (0 + 7) % 2 = 1 -> 'S' popped -> ['A']
    - Line 86: result = 'A'
    - Line 87: final = {"rel": "Affection", "emoji": "😊", "metric": "Crush Intensity"}
    """

    def test_john_and_mary_affection(self, flames_mod):
        inputs = ["john", "mary", "n"]
        stdout_buf = io.StringIO()

        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", stdout_buf):
            flames_mod.main()

        output = stdout_buf.getvalue()

        assert flames_mod.total_len == 8
        assert flames_mod.matched_chars == 0
        assert flames_mod.score == 30
        assert flames_mod.result == "A"
        assert flames_mod.final["rel"] == "Affection"
        assert "Remaining letters: 8" in output
        assert "Status: 😊 AFFECTION 😊" in output
        assert "Crush Intensity: 30%" in output


# ============================================================================
# Degenerate Case: identical names (count == 0)
# ============================================================================
class TestDegenerateCase:
    """Names sharing all characters cause count == 0; skipped with warning.

    Preconditions:
    - Line 62: if count == 0: valid_game = False (line 69)
    - Line 72: if valid_game: block is skipped entirely
    - Line 120: session["rounds"] == 0, session stats banner not shown
    """

    def test_degenerate_input(self, flames_mod):
        inputs = ["alex", "alex", "n"]
        stdout_buf = io.StringIO()

        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", stdout_buf):
            flames_mod.main()

        output = stdout_buf.getvalue()

        assert flames_mod.count == 0
        assert flames_mod.valid_game is False
        assert "DEGENERATE CASE DETECTED!" in output
        assert "These names share all letters! FLAMES is undefined." in output
        assert "MATCH REPORT CARD" not in output


# ============================================================================
# Verification of Documentation Example Execution
# ============================================================================
class TestDocumentationExample:
    """Verifies that the worked example in the documentation is executable and correct."""

    def test_docstring_exists_and_contains_worked_example(self, flames_mod):
        doc = flames_mod.main.__doc__
        assert doc is not None, "main() must have a docstring containing the worked example"
        assert "Worked Example" in doc or "Example" in doc
        # Decisive state transition explanation must be present
        assert "cyclic elimination" in doc.lower() or "elimination" in doc.lower()
        assert "modulo" in doc.lower() or "%" in doc

    def test_docstring_worked_example_matches_traced_execution(self, flames_mod):
        """Execute the exact inputs presented in the docstring and assert displayed output."""
        # The docstring uses ("a", "b", "n") as the minimal worked example
        inputs = ["a", "b", "n"]
        stdout_buf = io.StringIO()

        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", stdout_buf):
            flames_mod.main()

        output = stdout_buf.getvalue()

        # Assert key markers of the worked example's displayed output
        assert "FLAMES GAME - FIND YOUR RELATIONSHIP STATUS!" in output
        assert "Remaining letters: 2" in output
        assert "Status: 😈 ENEMIES 😈" in output
        assert "Rivalry Quotient: 30%" in output
        assert "Total Rounds Played : 1" in output
