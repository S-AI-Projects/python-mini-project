"""
Complexity and scaling regression tests for games/Minesweeper/minesweeper.py (Task R26-T049).

Anchors:
- NUMBERS = {0: "⬛", 1: "1️⃣", ...} (line 19)
- nr, nc = r + dr, c + dc (line 72)

Tests:
1. Smallest valid input: size=2, num_mines=1 -> 2x2 grid, 1 mine.
2. Ordinary input: size=5, num_mines=3 -> 5x5 grid, 3 mines, verified counts.
3. Scaling correctness across increasing grid sizes: N = 4, 8, 16.
"""

import importlib.util
import os
import random
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "games" / "Minesweeper" / "minesweeper.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("minesweeper_game", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["minesweeper_game"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestMinesweeperScaling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_anchor_preconditions(self):
        # Anchor check: NUMBERS mapping
        self.assertIn(0, self.mod.NUMBERS)
        self.assertEqual(self.mod.NUMBERS[1], "1️⃣")
        self.assertEqual(self.mod.NUMBERS[8], "8️⃣")

    def test_smallest_valid_input(self):
        # Smallest valid input: 2x2 board, 1 mine
        random.seed(42)
        game = self.mod.Minesweeper(size=2, num_mines=1)
        self.assertEqual(game.size, 2)
        self.assertEqual(game.num_mines, 1)
        self.assertEqual(len(game.grid), 2)
        self.assertEqual(len(game.grid[0]), 2)

        # Place mines with safe cell (0, 0)
        game.place_mines(safe_r=0, safe_c=0)

        # Verify exactly 1 mine placed
        mine_count = sum(row.count(-1) for row in game.grid)
        self.assertEqual(mine_count, 1)
        self.assertNotEqual(game.grid[0][0], -1)

    def test_ordinary_input_and_adjacency_verification(self):
        # Ordinary input: 5x5 board, 3 mines
        random.seed(123)
        game = self.mod.Minesweeper(size=5, num_mines=3)
        game.place_mines(safe_r=2, safe_c=2)

        # Count mines
        mine_count = sum(row.count(-1) for row in game.grid)
        self.assertEqual(mine_count, 3)

        # Verify adjacency math anchor: nr, nc = r + dr, c + dc
        for r in range(5):
            for c in range(5):
                if game.grid[r][c] == -1:
                    continue
                adjacent_mines = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and game.grid[nr][nc] == -1:
                            adjacent_mines += 1
                self.assertEqual(game.grid[r][c], adjacent_mines)

    def test_scaling_correctness_three_sizes(self):
        # Verify 3 increasing sizes: N = 4, 8, 16
        for size, mines in [(4, 2), (8, 6), (16, 20)]:
            random.seed(99)
            game = self.mod.Minesweeper(size=size, num_mines=mines)
            game.place_mines(safe_r=0, safe_c=0)
            actual_mines = sum(row.count(-1) for row in game.grid)
            self.assertEqual(actual_mines, mines)
            self.assertEqual(len(game.grid), size)
            self.assertEqual(len(game.grid[0]), size)


if __name__ == "__main__":
    unittest.main()
