"""
Boundary regression tests for utilities/Budget-Tracker/budget_tracker.py (Task R26-T042).

Validates the boundary behavior of initialize_file():
- Boundary 1 (Smallest valid input / Non-existent file): Creates file and writes FIELDNAMES header.
- Boundary 2 (Ordinary input / Existing file): Idempotent operation, preserves existing rows.
- Anchor preconditions:
  * FIELDNAMES = ["id", "date", "type", "category", "description", "amount"] (line 16)
  * transactions = [] (line 28)
"""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "utilities" / "Budget-Tracker" / "budget_tracker.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("budget_tracker", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["budget_tracker"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestBudgetTrackerBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_anchor_preconditions(self):
        # Anchor check: FIELDNAMES at line 16
        expected_fieldnames = ["id", "date", "type", "category", "description", "amount"]
        self.assertEqual(self.mod.FIELDNAMES, expected_fieldnames)

    def test_initialize_nonexistent_file_boundary(self):
        # Boundary: File does not exist yet -> should create file with exact FIELDNAMES header
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "new_budget.csv")
            self.assertFalse(os.path.exists(test_file))

            self.mod.initialize_file(test_file)

            self.assertTrue(os.path.exists(test_file))
            with open(test_file, "r", encoding="utf-8") as f:
                header = f.readline().strip()
            expected_header = ",".join(self.mod.FIELDNAMES)
            self.assertEqual(header, expected_header)

    def test_initialize_existing_file_idempotent_boundary(self):
        # Boundary: File already exists with transaction rows -> should not overwrite or truncate
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "existing_budget.csv")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("id,date,type,category,description,amount\n")
                f.write("1,2026-11-23,expense,Food,Lunch,15.50\n")

            # Call initialize_file on existing file
            self.mod.initialize_file(test_file)

            with open(test_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Ensure data was preserved
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[1].strip(), "1,2026-11-23,expense,Food,Lunch,15.50")


if __name__ == "__main__":
    unittest.main()
