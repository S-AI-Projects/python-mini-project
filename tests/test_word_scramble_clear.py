"""
Focused regression tests for `clear` in games/Word-Scramble-Game/Word-Scramble-Game.py.

Contract being verified:
- Source fixture preconditions:
    - note = []          (Word-Scramble-Game.py, line 276)
    - valid_words = []   (Word-Scramble-Game.py, line 345)
- Inputs: Optional mutable collection (e.g. list), or None (default).
- Return value: None.
- Mutation:
    - When target is provided, clears target in-place to [] (observable mutation).
    - When target is None, issues terminal clear command via os.system.
- Smallest valid input: [] (empty list), remains [] without error.
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


class TestWordScrambleClearRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()

    def test_a_smallest_valid_input(self):
        """Test A: Smallest valid input ([]), derived from note = [] (line 276)
        and valid_words = [] (line 345).
        """
        # Literal input representing smallest supported collection
        target_list = []
        original_id = id(target_list)

        actual_return = self.module.clear(target_list)

        # Assert exact returned value
        self.assertIsNone(
            actual_return,
            f"Expected return value None, but got {actual_return!r}",
        )
        # Assert observable mutation separately
        self.assertEqual(
            target_list,
            [],
            f"Expected list after execution to be [], but got {target_list!r}",
        )
        self.assertEqual(
            id(target_list),
            original_id,
            "Expected in-place mutation without reallocating list object",
        )

    def test_b_ordinary_input(self):
        """Test B: Ordinary input, derived from note entries (lines 277-278)."""
        target_list = ["hint used: −½ pts", "speed bonus: +½ pts"]
        original_id = id(target_list)

        actual_return = self.module.clear(target_list)

        # Assert exact returned value
        self.assertIsNone(
            actual_return,
            f"Expected return value None, but got {actual_return!r}",
        )
        # Assert expected state of the input after execution
        self.assertEqual(
            target_list,
            [],
            f"Expected list after execution to be [], but got {target_list!r}",
        )
        self.assertEqual(
            id(target_list),
            original_id,
            "Expected in-place mutation without reallocating list object",
        )

    def test_c_repeated_value_boundary(self):
        """Test C: Repeated-value input and domain boundary."""
        # 1. Repeated string values (duplicate note entries)
        repeated_notes = ["hint used: −½ pts", "hint used: −½ pts"]
        notes_id = id(repeated_notes)

        actual_return_notes = self.module.clear(repeated_notes)
        self.assertIsNone(
            actual_return_notes,
            f"Expected return value None, but got {actual_return_notes!r}",
        )
        self.assertEqual(
            repeated_notes,
            [],
            f"Expected list after execution to be [], but got {repeated_notes!r}",
        )
        self.assertEqual(id(repeated_notes), notes_id)

        # 2. Domain boundary with repeated structured tuples (mirroring valid_words, line 345)
        repeated_valid_words = [
            ("🐾 Animals", ["cat", "dog"]),
            ("🐾 Animals", ["cat", "dog"]),
        ]
        words_id = id(repeated_valid_words)

        actual_return_words = self.module.clear(repeated_valid_words)
        self.assertIsNone(
            actual_return_words,
            f"Expected return value None, but got {actual_return_words!r}",
        )
        self.assertEqual(
            repeated_valid_words,
            [],
            f"Expected list after execution to be [], but got {repeated_valid_words!r}",
        )
        self.assertEqual(id(repeated_valid_words), words_id)

    def test_d_preserve_public_interface_no_args(self):
        """Test D: Preserves existing zero-argument public interface for screen clearing."""
        with patch.object(os, "system") as mock_os_system:
            mock_os_system.return_value = 0
            actual_return = self.module.clear()

            self.assertIsNone(
                actual_return,
                f"Expected return value None, but got {actual_return!r}",
            )
            self.assertTrue(
                mock_os_system.called,
                "Expected os.system to be called when clear() is invoked with no arguments",
            )
            expected_cmd = "cls" if os.name == "nt" else "clear"
            mock_os_system.assert_called_with(expected_cmd)


if __name__ == "__main__":
    unittest.main()
