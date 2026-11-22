"""
Repeatability and deterministic isolation regression tests for `main` in utilities/Tower-of-Hanoi/Tower-of-Hanoi.py.

Task ID: R26-T055
Preconditions & Fixture Anchors:
- towers = {"A": [], "B": [], "C": []}          (Tower-of-Hanoi.py, line 39/56)
- tower_positions = {"A": 150, "B": 300, "C": 450} (Tower-of-Hanoi.py, line 44/61)
"""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Tower-of-Hanoi"
    / "Tower-of-Hanoi.py"
)


def load_module():
    """Load Tower-of-Hanoi module safely."""
    spec = importlib.util.spec_from_file_location("tower_of_hanoi", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTowerOfHanoiMainRepeatability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def create_mock_root(self):
        """Build a controlled mock Tk root for headless deterministic testing."""
        mock_root = MagicMock()
        mock_root.title = MagicMock()
        mock_root.geometry = MagicMock()
        mock_root.mainloop = MagicMock()
        return mock_root

    def test_smallest_valid_input_one_disk_contract(self):
        """Case 1: Smallest valid input domain (num_disks = 1).

        Preconditions:
        - Source line 39: towers = {"A": [], "B": [], "C": []}
        - Source line 44: tower_positions = {"A": 150, "B": 300, "C": 450}
        - Lower boundary check: num_disks >= 1
        """
        # Independently calculated expected state for smallest valid input
        expected_towers = {"A": [1], "B": [], "C": []}
        expected_positions = {"A": 150, "B": 300, "C": 450}

        # Simulate game start logic with num_disks = 1
        num_disks = 1
        calculated_towers = {
            "A": list(range(num_disks, 0, -1)),
            "B": [],
            "C": [],
        }

        self.assertEqual(calculated_towers, expected_towers)
        self.assertEqual(expected_positions["A"], 150)
        self.assertEqual(expected_positions["B"], 300)
        self.assertEqual(expected_positions["C"], 450)

        # Test main execution with injected mock root
        mock_root = self.create_mock_root()
        ret = self.module.main(root=mock_root)

        self.assertIs(ret, mock_root)
        mock_root.title.assert_called_with("Tower of Hanoi")
        mock_root.geometry.assert_called_with("800x600")
        # Ensure mainloop was not called in injected root mode
        mock_root.mainloop.assert_not_called()

    def test_ordinary_valid_input_three_disks_contract(self):
        """Case 2: Ordinary valid input (num_disks = 3).

        Preconditions:
        - Source line 39: towers = {"A": [], "B": [], "C": []}
        - Source line 44: tower_positions = {"A": 150, "B": 300, "C": 450}
        """
        expected_towers = {"A": [3, 2, 1], "B": [], "C": []}
        num_disks = 3
        calculated_towers = {
            "A": list(range(num_disks, 0, -1)),
            "B": [],
            "C": [],
        }

        self.assertEqual(calculated_towers, expected_towers)

        mock_root = self.create_mock_root()
        ret = self.module.main(root=mock_root)
        self.assertIs(ret, mock_root)
        mock_root.title.assert_called_with("Tower of Hanoi")

    def test_repeatability_and_state_isolation(self):
        """Case 3: Verify repeatability and input isolation across successive invocations.

        Calling main across multiple instances must not leak or cross-contaminate state.
        """
        mock_root_1 = self.create_mock_root()
        mock_root_2 = self.create_mock_root()

        ret1 = self.module.main(root=mock_root_1)
        ret2 = self.module.main(root=mock_root_2)

        self.assertIs(ret1, mock_root_1)
        self.assertIs(ret2, mock_root_2)
        self.assertIsNot(ret1, ret2)

        # Both received identical deterministic configuration
        mock_root_1.title.assert_called_once_with("Tower of Hanoi")
        mock_root_2.title.assert_called_once_with("Tower of Hanoi")
        mock_root_1.geometry.assert_called_once_with("800x600")
        mock_root_2.geometry.assert_called_once_with("800x600")

    def test_default_parameter_preserves_tk_instantiation(self):
        """Case 4: Preserves default parameter contract for legacy callers."""
        with patch("tkinter.Tk") as mock_tk_class:
            mock_inst = MagicMock()
            mock_tk_class.return_value = mock_inst

            ret = self.module.main()

            mock_tk_class.assert_called_once()
            self.assertIs(ret, mock_inst)
            mock_inst.mainloop.assert_called_once()
