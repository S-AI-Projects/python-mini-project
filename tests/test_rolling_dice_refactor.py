"""
Focused refactoring regression tests for games/Rolling-Dice/Rolling-Dice.py (Task R26-T046).

Verifies the extracted roll_dice() helper and main() flow:
- Precondition anchor: dice_emoji mapping (line 12).
- Smallest valid input: 'n' -> exits immediately.
- Ordinary input: 'y' followed by 'n' -> rolls two dice, displays emojis, and computes total.
- Invalid input: 'x' followed by 'n' -> displays warning and resumes loop.
"""

import importlib.util
import io
import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "games" / "Rolling-Dice" / "Rolling-Dice.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("rolling_dice", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rolling_dice"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestRollingDiceRefactor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_roll_dice_helper_output_and_range(self):
        # roll_dice returns tuple of 2 ints between 1 and 6
        for _ in range(25):
            d1, d2 = self.mod.roll_dice()
            self.assertIsInstance(d1, int)
            self.assertIsInstance(d2, int)
            self.assertIn(d1, range(1, 7))
            self.assertIn(d2, range(1, 7))

    def test_smallest_valid_input_exit(self):
        # Smallest valid input: 'n' exits cleanly
        with patch("builtins.input", side_effect=["n"]), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            self.mod.main()
            out = fake_out.getvalue()

        self.assertIn("Thanks for playing! See you next time!", out)
        self.assertNotIn("Rolling...", out)

    def test_ordinary_input_roll_then_exit(self):
        # Ordinary input: 'y', then 'n'
        with patch("builtins.input", side_effect=["y", "n"]), \
             patch.object(self.mod, "roll_dice", return_value=(3, 5)), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            self.mod.main()
            out = fake_out.getvalue()

        self.assertIn("Dice 1: 3 ⚂", out)
        self.assertIn("Dice 2: 5 ⚄", out)
        self.assertIn("Total: 8", out)
        self.assertIn("Thanks for playing! See you next time!", out)

    def test_invalid_input_handling(self):
        # Invalid input: 'maybe', then 'n'
        with patch("builtins.input", side_effect=["maybe", "n"]), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            self.mod.main()
            out = fake_out.getvalue()

        self.assertIn("Invalid input!! Please enter 'y' or 'n'.", out)


if __name__ == "__main__":
    unittest.main()
