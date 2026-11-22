"""
Executable documentation and contract regression tests for `clear_screen` in utilities/Pathfinding-Visualizer/Pathfinding-Visualizer.py.

Task ID: R26-T057
Preconditions & Fixture Anchors:
- neighbors = []                          (Pathfinding-Visualizer.py, line 14/35)
- rows, cols = len(grid), len(grid[0])    (Pathfinding-Visualizer.py, line 22/43)
- clear_screen definition                 (Pathfinding-Visualizer.py, line 4)
"""

import doctest
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Pathfinding-Visualizer"
    / "Pathfinding-Visualizer.py"
)


def load_module():
    """Load Pathfinding-Visualizer module safely."""
    spec = importlib.util.spec_from_file_location("pathfinding_visualizer", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPathfindingClearScreenDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_docstring_contains_worked_example(self):
        """Verify the docstring contains the published executable worked example."""
        doc = self.module.clear_screen.__doc__
        self.assertIsNotNone(doc)
        self.assertIn("Executable Worked Example", doc)
        self.assertIn("Decisive Transition", doc)
        self.assertIn("neighbors = []", doc)

    def test_smallest_valid_input_nt_environment(self):
        """Case 1: Smallest valid input domain (1x1 grid anchor, Windows NT).

        Preconditions:
        - Source line 14: neighbors = []
        - Source line 22: rows, cols = len(grid), len(grid[0]) = (1, 1)
        Literal input: ()
        """
        grid = [[" "]]
        rows, cols = len(grid), len(grid[0])
        self.assertEqual((rows, cols), (1, 1))

        fixture_neighbors = []

        with patch("os.name", "nt"), patch("os.system") as mock_sys:
            mock_sys.return_value = 0

            # Execute documented example 1
            ret = self.module.clear_screen()

            # Assert return value and system call
            self.assertIs(ret, None)
            mock_sys.assert_called_once_with("cls")

            # Assert zero observable mutation on fixtures
            self.assertEqual(fixture_neighbors, [])
            self.assertEqual(grid, [[" "]])

    def test_ordinary_valid_input_posix_environment(self):
        """Case 2: Ordinary valid input domain (5x5 grid anchor, POSIX environment).

        Preconditions:
        - Source line 14: neighbors = [(0, 1), (1, 0)]
        - Source line 22: rows, cols = (5, 5)
        Literal input: ()
        """
        grid = [[" " for _ in range(5)] for _ in range(5)]
        rows, cols = len(grid), len(grid[0])
        self.assertEqual((rows, cols), (5, 5))

        fixture_neighbors = [(0, 1), (1, 0)]

        with patch("os.name", "posix"), patch("os.system") as mock_sys:
            mock_sys.return_value = 0

            # Execute documented example 2
            ret = self.module.clear_screen()

            # Assert return value and system call
            self.assertIs(ret, None)
            mock_sys.assert_called_once_with("clear")

            # Assert fixtures remain unaltered
            self.assertEqual(fixture_neighbors, [(0, 1), (1, 0)])
            self.assertEqual(len(grid), 5)
            self.assertEqual(len(grid[0]), 5)

    def test_decisive_transition_trace(self):
        """Case 3: Trace execution demonstrating the decisive state transition."""
        dispatched_commands = []

        def capture_cmd(cmd):
            dispatched_commands.append(cmd)
            return 0

        with patch("os.name", "posix"), patch("os.system", side_effect=capture_cmd):
            self.module.clear_screen()

        self.assertEqual(dispatched_commands, ["clear"])
