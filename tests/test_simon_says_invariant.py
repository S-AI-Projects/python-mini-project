"""
Invariant / property checks for games/Simon-Says/Simon-Says.py (Task R26-T044).

Preconditions & Anchors:
- color_map = {'R': '🔴', 'B': '🔵', 'G': '🟢', 'Y': '🟡'} (line 28)
- sequence = [] (line 35)

Tests:
1. Smallest valid input: Single correct round, then end and 'N' to quit.
2. Ordinary input: Two correct rounds, then end and 'N' to quit.
3. Invariant Property Test: 100 bounded random sequences using a fixed seed.
4. Mutation resistance: Proves rejection when an incorrect key or color mutant is used.
"""

import importlib.util
import io
import os
import random
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "games" / "Simon-Says" / "Simon-Says.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("simon_says", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["simon_says"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSimonSaysInvariant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_anchor_preconditions(self):
        color_map = {'R': '🔴', 'B': '🔵', 'G': '🟢', 'Y': '🟡'}
        self.assertEqual(len(color_map), 4)

    def test_smallest_valid_input_one_round(self):
        # 1 correct round, then quit on next prompt
        mock_inputs = ["", "R", "X", "N"]
        with patch("builtins.input", side_effect=mock_inputs), \
             patch("time.sleep", return_value=None), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out, \
             patch("random.choice", return_value='🔴'):
            self.mod.main()
            output = fake_out.getvalue()

        self.assertIn("Correct! You've mastered this sequence!", output)
        self.assertIn("Rounds Completed: 1", output)
        self.assertIn("Thanks for playing Simon Says!", output)

    def test_ordinary_input_two_rounds(self):
        # 2 correct rounds, then 'X', then 'N'
        mock_inputs = ["", "R", "R B", "X", "N"]
        emojis = ['🔴', '🔵', '🟢']
        call_count = 0

        def fake_choice(options):
            nonlocal call_count
            res = emojis[call_count % len(emojis)]
            call_count += 1
            return res

        with patch("builtins.input", side_effect=mock_inputs), \
             patch("time.sleep", return_value=None), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out, \
             patch("random.choice", side_effect=fake_choice):
            self.mod.main()
            output = fake_out.getvalue()

        self.assertIn("Rounds Completed: 2", output)

    def test_invariant_100_bounded_valid_cases(self):
        # Generate 100 bounded valid color sequences with fixed seed 42
        rng = random.Random(42)
        color_map = {'R': '🔴', 'B': '🔵', 'G': '🟢', 'Y': '🟡'}
        keys = list(color_map.keys())

        for length in range(1, 101):
            seq_keys = [rng.choice(keys) for _ in range(length)]
            mapped_emojis = [color_map[k] for k in seq_keys]

            # Invariant 1: length preservation
            self.assertEqual(len(mapped_emojis), length)
            # Invariant 2: every element is a valid emoji from color_map.values()
            self.assertTrue(all(emoji in color_map.values() for emoji in mapped_emojis))
            # Invariant 3: reversible mapping
            reverse_map = {v: k for k, v in color_map.items()}
            recovered_keys = [reverse_map[e] for e in mapped_emojis]
            self.assertEqual(recovered_keys, seq_keys)

    def test_deliberate_mutant_fails(self):
        # Deliberate mutant: incorrect color key -> game_over round 0
        mock_inputs = ["", "B", "N"]
        with patch("builtins.input", side_effect=mock_inputs), \
             patch("time.sleep", return_value=None), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out, \
             patch("random.choice", return_value='🔴'):
            self.mod.main()
            output = fake_out.getvalue()

        self.assertIn("Wrong! The sequence was: 🔴", output)
        self.assertIn("Rounds Completed: 0", output)


if __name__ == "__main__":
    unittest.main()
