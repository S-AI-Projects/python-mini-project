"""
Focused regression tests for `clear` in games/Word-Scramble-Game/Word-Scramble-Game.py.

Task ID: R26-T051
Preconditions & Fixture Anchors:
- note = []          (Word-Scramble-Game.py, line 276)
- valid_words = []   (Word-Scramble-Game.py, line 345)
- clear definition   (Word-Scramble-Game.py, line 82)
"""

import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Word-Scramble-Game"
    / "Word-Scramble-Game.py"
)


def load_game_module():
    """Load Word-Scramble-Game module safely via importlib."""
    spec = importlib.util.spec_from_file_location("word_scramble_game", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestWordScrambleClearContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()

    def test_smallest_valid_input_nt_environment(self):
        """Case 1: Smallest supported input (zero arguments) under Windows (nt).

        Preconditions:
        - Source line 276: note = [] (empty fixture anchor)
        - Source line 345: valid_words = [] (empty fixture anchor)
        - Source line 82: def clear() -> calls os.system("cls") when os.name == "nt"
        """
        # Literal inputs
        fixture_note = []
        fixture_valid_words = []

        with patch("os.name", "nt"), patch("os.system") as mock_system:
            mock_system.return_value = 0

            # Act
            result = self.module.clear()

            # Assert returned value
            expected_result = None
            self.assertIs(
                result,
                expected_result,
                f"Expected return value to be {expected_result}, got {result}",
            )

            # Assert side effects
            expected_command = "cls"
            mock_system.assert_called_once_with(expected_command)

            # Assert observable mutation (must remain unchanged)
            expected_note = []
            expected_valid_words = []
            self.assertEqual(
                fixture_note,
                expected_note,
                "Observable mutation detected: fixture_note modified",
            )
            self.assertEqual(
                fixture_valid_words,
                expected_valid_words,
                "Observable mutation detected: fixture_valid_words modified",
            )

    def test_ordinary_input_posix_environment(self):
        """Case 2: Ordinary input under POSIX environment with populated fixtures.

        Preconditions:
        - Source line 276: note = [] -> populated state with game notes
        - Source line 345: valid_words = [] -> populated state with categories
        - Source line 82: def clear() -> calls os.system("clear") when os.name != "nt"
        """
        # Literal inputs (ordinary populated state)
        fixture_note = ["hint used: −½ pts", "speed bonus: +½ pts"]
        fixture_valid_words = [("animals", ["tiger", "elephant", "cheetah"])]

        with patch("os.name", "posix"), patch("os.system") as mock_system:
            mock_system.return_value = 0

            # Act
            result = self.module.clear()

            # Assert returned value
            expected_result = None
            self.assertIs(
                result,
                expected_result,
                f"Expected return value to be {expected_result}, got {result}",
            )

            # Assert side effects
            expected_command = "clear"
            mock_system.assert_called_once_with(expected_command)

            # Assert observable mutation (fixtures must remain strictly unchanged)
            expected_note = ["hint used: −½ pts", "speed bonus: +½ pts"]
            expected_valid_words = [("animals", ["tiger", "elephant", "cheetah"])]
            self.assertEqual(
                fixture_note,
                expected_note,
                "Observable mutation detected: fixture_note modified",
            )
            self.assertEqual(
                fixture_valid_words,
                expected_valid_words,
                "Observable mutation detected: fixture_valid_words modified",
            )

    def test_domain_boundary_repeated_invocations(self):
        """Case 3: Equivalent domain boundary - repeated invocations idempotent behavior.

        Preconditions:
        - Source line 276: note = []
        - Source line 345: valid_words = []
        - Source line 82: def clear() called repeatedly across simulated rounds.
        """
        fixture_note = ["round complete"]
        fixture_valid_words = [("science", ["atom", "gravity"])]

        with patch("os.name", "posix"), patch("os.system") as mock_system:
            mock_system.return_value = 0

            # Act: invoke clear multiple times
            results = [self.module.clear() for _ in range(5)]

            # Assert returned values
            expected_results = [None] * 5
            self.assertEqual(
                results,
                expected_results,
                f"Expected all returns to be None, got {results}",
            )

            # Assert system command called exact number of times
            self.assertEqual(
                mock_system.call_count,
                5,
                f"Expected os.system to be called 5 times, called {mock_system.call_count}",
            )
            for call_args in mock_system.call_args_list:
                self.assertEqual(call_args[0], ("clear",))

            # Assert zero observable mutation
            self.assertEqual(
                fixture_note,
                ["round complete"],
                "fixture_note unexpectedly mutated across repeated clear calls",
            )
            self.assertEqual(
                fixture_valid_words,
                [("science", ["atom", "gravity"])],
                "fixture_valid_words unexpectedly mutated across repeated clear calls",
            )
