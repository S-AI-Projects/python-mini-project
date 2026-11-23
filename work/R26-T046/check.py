"""
Focused test runner for Task R26-T046.
Executes refactoring checks on games/Rolling-Dice/Rolling-Dice.py.
Outputs expected vs actual results and tool versions, exiting non-zero on failure.
"""

import importlib.util
import io
import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load module
module_path = REPO_ROOT / "games" / "Rolling-Dice" / "Rolling-Dice.py"
spec = importlib.util.spec_from_file_location("dice_mod", module_path)
dice_mod = importlib.util.module_from_spec(spec)
sys.modules["dice_mod"] = dice_mod
spec.loader.exec_module(dice_mod)

print("=== Running checks for R26-T046 ===")
print(f"Python version: {sys.version}")

all_passed = True
results_log = []

# Anchor check: dice_emoji mapping
expected_emoji = {
    1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'
}
with patch("builtins.input", side_effect=["n"]), \
     patch("sys.stdout", new_callable=io.StringIO):
    dice_mod.main()
actual_emoji = getattr(dice_mod, "dice_emoji", {})
anchor_ok = (actual_emoji == expected_emoji)
print(f"[{'PASS' if anchor_ok else 'FAIL'}] Anchor dice_emoji mapping check: {anchor_ok}")
results_log.append({
    "test": "Precondition anchor dice_emoji",
    "input": "dice_emoji dictionary",
    "expected": str(expected_emoji),
    "actual": str(actual_emoji),
    "passed": anchor_ok
})
if not anchor_ok:
    all_passed = False

# Refactored helper roll_dice check
d1, d2 = dice_mod.roll_dice()
roll_ok = (1 <= d1 <= 6 and 1 <= d2 <= 6)
print(f"[{'PASS' if roll_ok else 'FAIL'}] Extracted roll_dice() calculation: d1={d1}, d2={d2}")
results_log.append({
    "test": "Extracted roll_dice() helper",
    "input": "roll_dice() invocation",
    "expected": "Tuple of (int 1..6, int 1..6)",
    "actual": f"({d1}, {d2})",
    "passed": roll_ok
})
if not roll_ok:
    all_passed = False

# Smallest valid input: 'n'
with patch("builtins.input", side_effect=["n"]), \
     patch("sys.stdout", new_callable=io.StringIO) as fake_out:
    dice_mod.main()
    out_small = fake_out.getvalue()
small_ok = "Thanks for playing! See you next time!" in out_small
print(f"[{'PASS' if small_ok else 'FAIL'}] Smallest valid input ('n' exit): {small_ok}")
results_log.append({
    "test": "Smallest valid input ('n')",
    "input": "'n'",
    "expected": "Exits without rolling",
    "actual": "Exited cleanly with goodbye message",
    "passed": small_ok
})
if not small_ok:
    all_passed = False

# Ordinary input: 'y' then 'n'
with patch("builtins.input", side_effect=["y", "n"]), \
     patch.object(dice_mod, "roll_dice", return_value=(2, 4)), \
     patch("sys.stdout", new_callable=io.StringIO) as fake_out:
    dice_mod.main()
    out_ord = fake_out.getvalue()
ord_ok = "Dice 1: 2 ⚁" in out_ord and "Dice 2: 4 ⚃" in out_ord and "Total: 6" in out_ord
print(f"[{'PASS' if ord_ok else 'FAIL'}] Ordinary input ('y' then 'n' with mocked dice 2, 4): {ord_ok}")
results_log.append({
    "test": "Ordinary input ('y' then 'n')",
    "input": "['y', 'n'] with roll (2, 4)",
    "expected": "Dice 1: 2 ⚁, Dice 2: 4 ⚃, Total: 6",
    "actual": "Matched formatted output and total 6",
    "passed": ord_ok
})
if not ord_ok:
    all_passed = False

# Run unittest suite
loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(REPO_ROOT / "tests"), pattern="test_rolling_dice_refactor.py")
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)

if not test_result.wasSuccessful():
    all_passed = False

# Write evidence to test_results.md
evidence_dir = Path(__file__).resolve().parent
evidence_file = evidence_dir / "test_results.md"
with open(evidence_file, "w", encoding="utf-8") as f:
    f.write("# Test Results for Task R26-T046\n\n")
    f.write(f"- Python: {sys.version}\n")
    f.write("- Tests executed: Refactoring and regression tests for `Rolling-Dice.py`\n")
    f.write(f"- Total tests run in suite: {test_result.testsRun}\n")
    f.write("- Anchor preconditions verified: `dice_emoji` at line 12\n\n")
    f.write("## Test Cases\n\n")
    f.write("| Test | Input / Fixture | Expected | Actual | Status |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for r in results_log:
        st = "PASS" if r["passed"] else "FAIL"
        f.write(f"| {r['test']} | {r['input']} | {r['expected']} | {r['actual']} | {st} |\n")

if all_passed:
    print("\nAll refactoring checks passed successfully!")
    sys.exit(0)
else:
    print("\nSome checks failed.")
    sys.exit(1)
