"""
Executable documentation tests for math/Projectile-Motion-Game/Projectile-Motion-Game.py (Task R26-T047).

Executes and asserts the documented worked example and state transitions:
- Smallest valid input fixture: speed = 1.0 m/s, angle = 1.0 deg
- Ordinary input fixture: speed = 10.0 m/s, angle = 45.0 deg
- Asserts intermediate states (angle in radians, sin calculations) and decisive physical outputs.
- Executes main() with mocked CLI/GUI and asserts displayed results match documentation.
"""

import importlib.util
import io
import math
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path


class MockArray:
    def __init__(self, data):
        self.data = list(data) if isinstance(data, (list, tuple)) else [data]

    def __mul__(self, other):
        if isinstance(other, MockArray):
            return MockArray([a * b for a, b in zip(self.data, other.data)])
        return MockArray([a * other for a in self.data])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, MockArray):
            return MockArray([a - b for a, b in zip(self.data, other.data)])
        return MockArray([a - other for a in self.data])

    def __rsub__(self, other):
        return MockArray([other - a for a in self.data])

    def __pow__(self, power):
        return MockArray([a ** power for a in self.data])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return MockArray(self.data[item])
        return self.data[item]

    def __iter__(self):
        return iter(self.data)


# Mock external optional GUI / numerical dependencies if not installed
for mod_name in ["numpy", "matplotlib", "matplotlib.pyplot", "matplotlib.animation"]:
    if mod_name not in sys.modules:
        try:
            __import__(mod_name)
        except ImportError:
            mock = MagicMock()
            if mod_name == "numpy":
                mock.linspace = lambda a, b, num: MockArray([a + i * (b - a) / (num - 1) for i in range(num)])
                mock.cos = math.cos
                mock.sin = math.sin
                mock.maximum = lambda arr, val: MockArray([max(x, val) for x in arr])
                mock.array = lambda lst: MockArray(lst)
            sys.modules[mod_name] = mock

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "math" / "Projectile-Motion-Game" / "Projectile-Motion-Game.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("projectile_game", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["projectile_game"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestProjectileMotionDocExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_precondition_gravity_constant(self):
        # Anchor precondition: GRAVITY = 9.81 (line 14)
        self.assertEqual(self.mod.GRAVITY, 9.81)

    def test_smallest_valid_input_metrics(self):
        # Smallest valid input: speed = 1.0, angle = 1.0
        tof, hmax, rng = self.mod.compute_trajectory_metrics(1.0, 1.0)
        self.assertAlmostEqual(tof, (2 * 1.0 * math.sin(math.radians(1.0))) / 9.81, places=5)
        self.assertAlmostEqual(hmax, (1.0**2 * math.sin(math.radians(1.0))**2) / (2 * 9.81), places=5)
        self.assertAlmostEqual(rng, (1.0**2 * math.sin(math.radians(2.0))) / 9.81, places=5)
        self.assertEqual(f"{tof:.2f}", "0.00")
        self.assertEqual(f"{hmax:.2f}", "0.00")
        self.assertEqual(f"{rng:.2f}", "0.00")

    def test_ordinary_worked_example_metrics(self):
        # Documented worked example: speed = 10.0, angle = 45.0
        tof, hmax, rng = self.mod.compute_trajectory_metrics(10.0, 45.0)
        self.assertEqual(f"{tof:.2f}", "1.44")
        self.assertEqual(f"{hmax:.2f}", "2.55")
        self.assertEqual(f"{rng:.2f}", "10.19")

    def test_main_cli_executes_documented_example(self):
        # Run main() selecting 1 (calculate), speed 10, angle 45, then 2 (exit)
        mock_inputs = ["1", "10", "45", "2"]
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_ax.plot.side_effect = [(MagicMock(),), (MagicMock(),)] * 10
        self.mod.plt.subplots = MagicMock(return_value=(mock_fig, mock_ax))
        self.mod.plt.show = MagicMock(return_value=None)

        with patch("builtins.input", side_effect=mock_inputs), \
             patch("time.sleep", return_value=None), \
             patch("sys.stdout", new_callable=io.StringIO) as fake_out:
            self.mod.main()
            out = fake_out.getvalue()

        # Assert displayed output matches documented worked example
        self.assertIn("Time of Flight (TOF) : 1.44 s", out)
        self.assertIn("Max Height (Hmax)    : 2.55 m", out)
        self.assertIn("Horizontal Range     : 10.19 m", out)
        self.assertIn("Exiting... See you next launch!", out)


if __name__ == "__main__":
    unittest.main()
