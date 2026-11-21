"""
Focused regression tests for `main` in games/Number-Guessing-Game/Number-Guessing-Game.py.

Task ID: R26-T052
Preconditions & Fixture Anchors:
- DIFFICULTY_ATTEMPTS = {"1": 15, "2": 10, "3": 5} (Number-Guessing-Game.py, lines 21-25)
- guess_history = []                               (Number-Guessing-Game.py, line 53)
- MIN_NUMBER = 1, MAX_NUMBER = 100                 (Number-Guessing-Game.py, lines 17-18)
"""

import importlib.util
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Number-Guessing-Game"
    / "Number-Guessing-Game.py"
)


def load_game_module():
    """Load Number-Guessing-Game module safely via importlib."""
    spec = importlib.util.spec_from_file_location("number_guessing_game", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestNumberGuessingMainDomain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()

    def run_main_with_inputs(self, inputs, mock_target_number):
        """Helper to run main with mocked inputs, target number, and captured stdout."""
        input_iter = iter(inputs)
        captured_out = io.StringIO()

        with patch("builtins.input", lambda *args: next(input_iter)), \
             patch("random.randint", return_value=mock_target_number), \
             patch("sys.stdout", captured_out):
            self.module.main()

        return captured_out.getvalue()

    def test_smallest_valid_input_immediate_win(self):
        """Test Case 1: Smallest valid input domain.

        Preconditions:
        - Line 24: DIFFICULTY_ATTEMPTS["3"] = 5 (smallest attempt budget)
        - Line 17: MIN_NUMBER = 1 (smallest valid target & guess)
        - Line 53: guess_history = []
        Literal inputs: ["3", "1", "n"] with target = 1
        """
        output = self.run_main_with_inputs(["3", "1", "n"], mock_target_number=1)

        self.assertIn(
            "You have 5 attempts.",
            output,
            "Expected 5 attempts allocated for difficulty '3' (line 24)",
        )
        self.assertIn(
            "🎉 Correct! You guessed the number.",
            output,
            "Expected correct guess message for target 1 (line 77)",
        )
        self.assertIn(
            "🎯 Attempts: 1/5",
            output,
            "Expected attempts count 1/5 (line 79)",
        )
        self.assertIn(
            "📜 Guesses: 1",
            output,
            "Expected guess_history to contain only [1] (lines 53, 74, 80)",
        )
        self.assertIn(
            "🏆 You solved it in 1 guesses.",
            output,
            "Expected solved in 1 guesses message (line 107)",
        )
        self.assertIn(
            "👋 Goodbye.",
            output,
            "Expected goodbye on 'n' choice (line 116)",
        )

    def test_ordinary_input_multi_guess_win(self):
        """Test Case 2: Ordinary input across domain interior.

        Preconditions:
        - Line 23: DIFFICULTY_ATTEMPTS["2"] = 10 (Medium difficulty)
        - Line 53: guess_history = []
        Literal inputs: ["2", "25", "75", "45", "50", "n"] with target = 50
        """
        output = self.run_main_with_inputs(
            ["2", "25", "75", "45", "50", "n"],
            mock_target_number=50,
        )

        self.assertIn(
            "You have 10 attempts.",
            output,
            "Expected 10 attempts for difficulty '2' (line 23)",
        )
        self.assertIn(
            "📈 Too low.",
            output,
            "Expected 'Too low.' for guess 25 < 50 (line 87)",
        )
        self.assertIn(
            "📉 Too high.",
            output,
            "Expected 'Too high.' for guess 75 > 50 (line 85)",
        )
        self.assertIn(
            "😊 Close.",
            output,
            "Expected 'Close.' proximity hint for guess 45 (abs diff 5 <= 10, line 94)",
        )
        self.assertIn(
            "🎉 Correct! You guessed the number.",
            output,
            "Expected victory message on guess 50 == 50 (line 77)",
        )
        self.assertIn(
            "🎯 Attempts: 4/10",
            output,
            "Expected attempts used: 4/10 (line 79)",
        )
        self.assertIn(
            "📜 Guesses: 25, 75, 45, 50",
            output,
            "Expected complete guess history [25, 75, 45, 50] (lines 53, 74, 80)",
        )
        self.assertIn(
            "🏆 You solved it in 4 guesses.",
            output,
            "Expected 4 guesses solved message (line 107)",
        )

    def test_lower_boundary_inside_and_outside(self):
        """Test Case 3: Lower boundary partition (0 rejected vs 1 accepted).

        Preconditions:
        - Line 17: MIN_NUMBER = 1
        - Line 69: if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):
        Literal inputs: ["3", "0", "1", "n"] with target = 1
        """
        output = self.run_main_with_inputs(["3", "0", "1", "n"], mock_target_number=1)

        self.assertIn(
            "⚠️ Enter a number between 1 and 100.",
            output,
            "Expected rejection warning for guess 0 below MIN_NUMBER (line 70)",
        )
        self.assertIn(
            "🎯 Attempts: 1/5",
            output,
            "Expected attempts count to be 1/5, proving guess 0 was not penalized (lines 69-73)",
        )
        self.assertIn(
            "📜 Guesses: 1",
            output,
            "Expected guess_history to only record valid guess [1], excluding 0 (lines 70, 74)",
        )

    def test_upper_boundary_inside_and_outside(self):
        """Test Case 4: Upper boundary partition (101 rejected vs 100 accepted).

        Preconditions:
        - Line 18: MAX_NUMBER = 100
        - Line 69: if not (MIN_NUMBER <= guess_num <= MAX_NUMBER):
        Literal inputs: ["3", "101", "100", "n"] with target = 100
        """
        output = self.run_main_with_inputs(["3", "101", "100", "n"], mock_target_number=100)

        self.assertIn(
            "⚠️ Enter a number between 1 and 100.",
            output,
            "Expected rejection warning for guess 101 above MAX_NUMBER (line 70)",
        )
        self.assertIn(
            "🎯 Attempts: 1/5",
            output,
            "Expected attempts count to be 1/5, proving guess 101 was not penalized (lines 69-73)",
        )
        self.assertIn(
            "📜 Guesses: 100",
            output,
            "Expected guess_history to only record valid guess [100], excluding 101 (lines 70, 74)",
        )

    def test_attempts_exhaustion_loss_boundary(self):
        """Test Case 5: Loss boundary (exhausting all max_attempts).

        Preconditions:
        - Line 24: DIFFICULTY_ATTEMPTS["3"] = 5
        - Line 59: while attempts < max_attempts:
        - Line 100: if not won:
        Literal inputs: ["3", "10", "20", "30", "40", "60", "n"] with target = 50
        """
        output = self.run_main_with_inputs(
            ["3", "10", "20", "30", "40", "60", "n"],
            mock_target_number=50,
        )

        self.assertIn(
            "💀 Out of attempts.",
            output,
            "Expected loss header on exhausting attempts (line 101)",
        )
        self.assertIn(
            "The number was 50.",
            output,
            "Expected revealing target number on loss (line 102)",
        )
        self.assertIn(
            "📜 Your guesses: 10, 20, 30, 40, 60",
            output,
            "Expected complete guess_history on loss (line 104)",
        )
        self.assertIn(
            "❌ You used all 5 attempts.",
            output,
            "Expected confirmation of all 5 attempts used (line 105)",
        )

    def test_difficulty_boundary_and_default(self):
        """Test Case 6: Difficulty selection boundary and default fallback.

        Preconditions:
        - Line 42: get_choice(choices=["1", "2", "3"], default="2")
        Literal inputs: ["4", "", "50", "n"] with target = 50
        """
        output = self.run_main_with_inputs(
            ["4", "", "50", "n"],
            mock_target_number=50,
        )

        self.assertIn(
            "⚠️ Invalid selection. Please enter 1, 2 or 3.",
            output,
            "Expected rejection for unsupported difficulty choice '4' (line 46)",
        )
        self.assertIn(
            "You have 10 attempts.",
            output,
            "Expected empty choice to resolve to default '2' (10 attempts, lines 23, 45)",
        )
        self.assertIn(
            "🎯 Attempts: 1/10",
            output,
            "Expected victory with attempts 1/10 (line 79)",
        )


if __name__ == "__main__":
    unittest.main()
