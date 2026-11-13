"""Tests for the Tip Calculator contract and runnable README example."""

import os
import re
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from main import calculate_split


PROJECT_DIR = Path(__file__).resolve().parent
README_PATH = PROJECT_DIR / "README.md"
EXPECTED_README_OUTPUT = (
    "Shares: $36.67, $36.67, $36.66\n"
    "Total: $110.00\n"
)


class TipCalculatorTests(unittest.TestCase):
    def test_bill_100_tip_10_split_three_ways(self):
        shares = calculate_split(Decimal("100"), Decimal("10"), 3)

        self.assertEqual(
            shares,
            [Decimal("36.67"), Decimal("36.67"), Decimal("36.66")],
        )
        self.assertEqual(sum(shares), Decimal("110.00"))

    def test_zero_bill_returns_zero_shares(self):
        self.assertEqual(
            calculate_split(Decimal("0"), Decimal("10"), 2),
            [Decimal("0.00"), Decimal("0.00")],
        )

    def test_bill_total_uses_half_up_currency_rounding(self):
        self.assertEqual(
            calculate_split(Decimal("0.005"), Decimal("0"), 1),
            [Decimal("0.01")],
        )

    def test_zero_people_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_split(Decimal("100"), Decimal("10"), 0)

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_split(Decimal("-1"), Decimal("10"), 2)

    def test_readme_python_example_has_documented_output(self):
        readme = README_PATH.read_text(encoding="utf-8")
        match = re.search(r"```python example\n(.*?)\n```", readme, re.DOTALL)
        self.assertIsNotNone(match, "README must contain a runnable example")

        result = subprocess.run(
            [sys.executable, "-c", match.group(1)],
            cwd=PROJECT_DIR,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, EXPECTED_README_OUTPUT)

    def test_cli_prints_split_for_stdin_example(self):
        result = subprocess.run(
            [sys.executable, str(PROJECT_DIR / "main.py")],
            input="100\n10\n3\n",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "💵 TIP CALCULATOR 💵\n"
            "Bill amount: Tip percentage: Number of people: "
            "Shares: $36.67, $36.67, $36.66\n"
            "Total: $110.00\n",
        )

    def test_import_has_no_prompt_or_filesystem_side_effect(self):
        with tempfile.TemporaryDirectory() as working_directory:
            script = (
                "import builtins, os, pathlib\n"
                "builtins.input = lambda *args: "
                "(_ for _ in ()).throw(AssertionError('unexpected prompt'))\n"
                "root = pathlib.Path(os.environ['TIP_CALC_DIR'])\n"
                "before = {path.name for path in root.iterdir()}\n"
                "import main\n"
                "assert not list(pathlib.Path('.').iterdir())\n"
                "assert before == {path.name for path in root.iterdir()}\n"
            )
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=working_directory,
                env={
                    **os.environ,
                    "PYTHONPATH": str(PROJECT_DIR),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "TIP_CALC_DIR": str(PROJECT_DIR),
                },
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
