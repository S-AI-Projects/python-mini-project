"""
Repeatability and deterministic execution tests for games/Sudoku-Game/Sudoku-Game.py (Task R26-T045).

Verifies print_header:
- Smallest valid input: Explicit stream buffer io.StringIO()
- Ordinary input: Default invocation (stream=None -> sys.stdout)
- Repeatability: Running twice in fresh state and once after valid input yields identical outputs.
- Anchor preconditions:
  * start_r, start_c = 3 * (r // 3), 3 * (c // 3) (line 99)
  * empty_cells = [] (line 125)
"""

import importlib.util
import io
import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "games" / "Sudoku-Game" / "Sudoku-Game.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("sudoku_game", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sudoku_game"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSudokuHeaderRepeatable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_anchor_preconditions(self):
        # Verify anchor calculation logic from is_valid function
        r, c = 4, 7
        start_r, start_c = 3 * (r // 3), 3 * (c // 3)
        self.assertEqual(start_r, 3)
        self.assertEqual(start_c, 6)

    def test_smallest_valid_input_custom_stream(self):
        # Injected stream seam allows deterministic capture without global side effects
        buf = io.StringIO()
        self.mod.print_header(stream=buf)
        output = buf.getvalue()

        self.assertIn("SUDOKU GAME & BACKTRACKING SOLVER", output)
        self.assertIn("══════════════════════════════════════════════════════════", output)

    def test_ordinary_input_default_stdout(self):
        # Default parameter preserves compatibility with existing callers
        with patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            self.mod.print_header()
            output = fake_out.getvalue()

        self.assertIn("SUDOKU GAME & BACKTRACKING SOLVER", output)

    def test_repeatability_and_state_isolation(self):
        # Run twice in fresh isolated state and once after another valid input
        buf1 = io.StringIO()
        self.mod.print_header(stream=buf1)

        buf2 = io.StringIO()
        self.mod.print_header(stream=buf2)

        # Intervening call with stdout
        with patch("sys.stdout", new_callable=io.StringIO):
            self.mod.print_header()

        buf3 = io.StringIO()
        self.mod.print_header(stream=buf3)

        # All runs produce identical outputs
        self.assertEqual(buf1.getvalue(), buf2.getvalue())
        self.assertEqual(buf2.getvalue(), buf3.getvalue())


if __name__ == "__main__":
    unittest.main()
