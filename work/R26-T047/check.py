"""
Focused test runner for Task R26-T047.
Executes documented worked example tests on math/Projectile-Motion-Game/Projectile-Motion-Game.py.
Outputs expected vs actual results and tool versions, exiting non-zero on failure.
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

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load module
module_path = REPO_ROOT / "math" / "Projectile-Motion-Game" / "Projectile-Motion-Game.py"
spec = importlib.util.spec_from_file_location("proj_mod", module_path)
proj_mod = importlib.util.module_from_spec(spec)
sys.modules["proj_mod"] = proj_mod
spec.loader.exec_module(proj_mod)

print("=== Running checks for R26-T047 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Precondition check: GRAVITY
grav = proj_mod.GRAVITY
grav_ok = (grav == 9.81)
print(f"[{'PASS' if grav_ok else 'FAIL'}] Anchor GRAVITY == 9.81 (line 14): {grav_ok}")
results_log.append({
    "test": "Precondition anchor GRAVITY",
    "input": "GRAVITY",
    "expected": "9.81",
    "actual": str(grav),
    "passed": grav_ok
})
if not grav_ok:
    all_passed = False

# Smallest valid input: speed=1.0, angle=1.0
tof_s, hmax_s, rng_s = proj_mod.compute_trajectory_metrics(1.0, 1.0)
s_ok = (f"{tof_s:.2f}" == "0.00" and f"{hmax_s:.2f}" == "0.00" and f"{rng_s:.2f}" == "0.00")
print(f"[{'PASS' if s_ok else 'FAIL'}] Smallest valid input (1.0 m/s, 1.0 deg): TOF={tof_s:.2f}s, Hmax={hmax_s:.2f}m, Range={rng_s:.2f}m")
results_log.append({
    "test": "Smallest valid input (1.0 m/s, 1.0 deg)",
    "input": "speed=1.0, angle=1.0",
    "expected": "TOF=0.00s, Hmax=0.00m, Range=0.00m",
    "actual": f"TOF={tof_s:.2f}s, Hmax={hmax_s:.2f}m, Range={rng_s:.2f}m",
    "passed": s_ok
})
if not s_ok:
    all_passed = False

# Ordinary worked example: speed=10.0, angle=45.0
tof_o, hmax_o, rng_o = proj_mod.compute_trajectory_metrics(10.0, 45.0)
o_ok = (f"{tof_o:.2f}" == "1.44" and f"{hmax_o:.2f}" == "2.55" and f"{rng_o:.2f}" == "10.19")
print(f"[{'PASS' if o_ok else 'FAIL'}] Ordinary worked example (10.0 m/s, 45.0 deg): TOF={tof_o:.2f}s, Hmax={hmax_o:.2f}m, Range={rng_o:.2f}m")
results_log.append({
    "test": "Ordinary worked example (10.0 m/s, 45.0 deg)",
    "input": "speed=10.0, angle=45.0",
    "expected": "TOF=1.44s, Hmax=2.55m, Range=10.19m",
    "actual": f"TOF={tof_o:.2f}s, Hmax={hmax_o:.2f}m, Range={rng_o:.2f}m",
    "passed": o_ok
})
if not o_ok:
    all_passed = False

# Execute main() and verify displayed output matches documentation
mock_inputs = ["1", "10", "45", "2"]
mock_fig = MagicMock()
mock_ax = MagicMock()
mock_ax.plot.side_effect = [(MagicMock(),), (MagicMock(),)] * 10
proj_mod.plt.subplots = MagicMock(return_value=(mock_fig, mock_ax))
proj_mod.plt.show = MagicMock(return_value=None)

with patch("builtins.input", side_effect=mock_inputs), \
     patch("time.sleep", return_value=None), \
     patch("sys.stdout", new_callable=io.StringIO) as fake_out:
    proj_mod.main()
    out = fake_out.getvalue()

main_ok = ("Time of Flight (TOF) : 1.44 s" in out and
           "Max Height (Hmax)    : 2.55 m" in out and
           "Horizontal Range     : 10.19 m" in out)
print(f"[{'PASS' if main_ok else 'FAIL'}] main() execution asserts documented worked example output: {main_ok}")
results_log.append({
    "test": "main() CLI execution check",
    "input": "Interactive input ['1', '10', '45', '2']",
    "expected": "TOF=1.44s, Hmax=2.55m, Range=10.19m",
    "actual": "Matched formatted results in stdout",
    "passed": main_ok
})
if not main_ok:
    all_passed = False

# Run unittest suite
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "tests"), pattern="test_projectile_motion_doc_example.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T047\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: Executable worked example tests for `Projectile-Motion-Game.py`\n")
    f.write(f"- Total tests run in suite: {test_result.testsRun}\n")
    f.write("- Anchor preconditions verified: `GRAVITY = 9.81` (line 14)\n\n")
    f.write("## Test Cases\n\n")
    f.write("| Test | Input / Fixture | Expected | Actual | Status |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['test']} | {r['input']} | {r['expected']} | {r['actual']} | {st} |\n")

if all_passed:
    print("\nAll executable documentation checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
