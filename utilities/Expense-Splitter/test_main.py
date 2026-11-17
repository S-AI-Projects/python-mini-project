import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("main.py")
SPEC = importlib.util.spec_from_file_location("expense_splitter_main", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExpenseSplitterTests(unittest.TestCase):
    def test_split_amount_rounds_evenly(self):
        self.assertEqual(MODULE.split_amount(120, 4), 30.0)
        self.assertEqual(MODULE.split_amount(100, 3), 33.33)

    def test_split_amount_rejects_invalid_input(self):
        with self.assertRaises(ValueError):
            MODULE.split_amount(-10, 2)
        with self.assertRaises(ValueError):
            MODULE.split_amount(50, 0)

    def test_calculate_balances_for_shared_expense(self):
        records = [
            {"payer": "Alice", "amount": 60, "participants": ["Alice", "Bob", "Carol"]}
        ]

        self.assertEqual(
            MODULE.calculate_balances(records),
            {"Alice": 40.0, "Bob": -20.0, "Carol": -20.0},
        )

    def test_settle_debts_returns_minimal_transfers(self):
        records = [
            {"payer": "Alice", "amount": 60, "participants": ["Alice", "Bob", "Carol"]}
        ]

        self.assertEqual(
            MODULE.settle_debts(records),
            [
                {"from": "Bob", "to": "Alice", "amount": 20.0},
                {"from": "Carol", "to": "Alice", "amount": 20.0},
            ],
        )

    def test_parse_expense_entry_accepts_colon_format(self):
        entry = MODULE.parse_expense_entry("Alice:90:Bob,Carol")
        self.assertEqual(entry, {"payer": "Alice", "amount": 90.0, "participants": ["Bob", "Carol"]})

    def test_cli_summary_matches_expected_values(self):
        result = MODULE.main([
            "--expense",
            "Alice:90:Bob,Carol",
            "--expense",
            "Bob:50:Alice,Carol",
        ])

        self.assertEqual(result["balances"], {"Alice": 65.0, "Bob": 5.0, "Carol": -70.0})
        self.assertEqual(result["settlements"][0], {"from": "Carol", "to": "Alice", "amount": 65.0})
        self.assertEqual(result["settlements"][1], {"from": "Carol", "to": "Bob", "amount": 5.0})

    def test_format_report_uses_injected_clock_for_repeatability(self):
        class FakeClock:
            def now(self):
                return datetime(2024, 1, 2, 3, 4, 5)

        report = MODULE.format_report(
            [{"payer": "Alice", "amount": 60, "participants": ["Alice", "Bob", "Carol"]}],
            clock=FakeClock(),
        )

        self.assertIn("Generated at: 2024-01-02T03:04:05", report)

    def test_choose_random_payer_and_save_report_are_injectable(self):
        class FakeRNG:
            def choice(self, sequence):
                return sequence[0]

        self.assertEqual(MODULE.choose_random_payer(["Alice", "Bob", "Carol"], rng=FakeRNG()), "Alice")

        written = {}

        def fake_writer(path, content):
            written[path] = content

        saved_path = MODULE.save_report("hello", "/tmp/expense-report.txt", file_writer=fake_writer)
        self.assertEqual(saved_path, "/tmp/expense-report.txt")
        self.assertEqual(written["/tmp/expense-report.txt"], "hello")


if __name__ == "__main__":
    unittest.main()
