"""Unittest checks for the Leap Year Calendar utility."""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from main import days_in_month, is_leap_year, main


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = REPO_ROOT / "work" / "R26-T028"


class LeapYearCalendarChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case_results = []
        WORK_DIR.mkdir(parents=True, exist_ok=True)
        (WORK_DIR / "case-results.jsonl").unlink(missing_ok=True)

    def record(self, check, inputs, expected, actual, status="passed", message=None):
        self.case_results.append(
            {
                "check": check,
                "inputs": inputs,
                "expected": expected,
                "actual": actual,
                "status": status,
                "message": message,
            }
        )

    def tearDown(self):
        for result in self.case_results[self._case_start:]:
            with (WORK_DIR / "case-results.jsonl").open("a", encoding="utf-8") as file:
                file.write(json.dumps(result) + "\n")
        self._case_start = len(self.case_results)

    def setUp(self):
        self._case_start = len(self.case_results)

    def assert_exception_case(self, check, inputs, call, exception_type, message):
        try:
            call()
        except exception_type as error:
            actual = {"type": type(error).__name__, "message": str(error)}
            expected = {"type": exception_type.__name__, "message": message}
            self.assertEqual(actual, expected)
            self.record(check, inputs, expected, actual)
        else:
            actual = None
            expected = {"type": exception_type.__name__, "message": message}
            self.record(
                check,
                inputs,
                expected,
                actual,
                status="failed",
                message=f"Did not raise {exception_type.__name__}",
            )
            self.fail(f"{check} did not raise {exception_type.__name__}")

    def test_leap_year_acceptance_cases(self):
        cases = [
            (1900, False),
            (2000, True),
            (2023, False),
            (2024, True),
        ]
        for year, expected in cases:
            actual = is_leap_year(year)
            self.assertIs(actual, expected)
            self.record(
                "is_leap_year",
                {"year": year},
                expected,
                actual,
            )

    def test_days_in_month_acceptance_cases(self):
        cases = [
            (2024, 2, 29),
            (2023, 2, 28),
            (2024, 4, 30),
            (2024, 12, 31),
        ]
        for year, month, expected in cases:
            actual = days_in_month(year, month)
            self.assertEqual(actual, expected)
            self.record(
                "days_in_month",
                {"year": year, "month": month},
                expected,
                actual,
            )

    def test_year_type_validation(self):
        self.assert_exception_case(
            "is_leap_year_invalid_bool",
            {"year": True},
            lambda: is_leap_year(True),
            TypeError,
            "Invalid year type 'bool': expected an integer between 1 and 9999.",
        )

    def test_year_range_validation(self):
        self.assert_exception_case(
            "is_leap_year_invalid_range",
            {"year": 0},
            lambda: is_leap_year(0),
            ValueError,
            "Invalid year 0: expected an integer between 1 and 9999.",
        )

    def test_month_validation(self):
        self.assert_exception_case(
            "days_in_month_invalid_month",
            {"year": 2024, "month": 13},
            lambda: days_in_month(2024, 13),
            ValueError,
            "Invalid month 13: expected an integer between 1 and 12.",
        )

    def test_failed_call_leaves_caller_data_and_file_unchanged(self):
        caller_data = {"year": 2024, "month": 13, "records": [1, 2, 3]}
        original_data = {
            "year": caller_data["year"],
            "month": caller_data["month"],
            "records": caller_data["records"].copy(),
        }

        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "calendar.txt"
            file_path.write_text("unchanged", encoding="utf-8")
            original_file = file_path.read_bytes()

            with self.assertRaises(ValueError):
                days_in_month(caller_data["year"], caller_data["month"])

            self.assertEqual(caller_data, original_data)
            self.assertEqual(file_path.read_bytes(), original_file)
            self.record(
                "failure_integrity",
                {
                    "caller_data": caller_data,
                    "file_before": original_file.decode("utf-8"),
                },
                {"caller_data": original_data, "file_after": "unchanged"},
                {
                    "caller_data": caller_data,
                    "file_after": file_path.read_text(encoding="utf-8"),
                },
            )

    def test_cli_success_output(self):
        cases = [
            (["2000"], "2000 is a leap year."),
            (["1900"], "1900 is not a leap year."),
            (["2024", "2"], "February 2024 has 29 days."),
            (["2023", "2"], "February 2023 has 28 days."),
        ]
        for argv, expected_output in cases:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(argv)
            actual = {
                "exit_code": exit_code,
                "stdout": stdout.getvalue(),
                "stderr": stderr.getvalue(),
            }
            expected = {
                "exit_code": 0,
                "stdout": expected_output + "\n",
                "stderr": "",
            }
            self.assertEqual(actual, expected)
            self.record("cli_success", argv, expected, actual)

    def test_cli_invalid_output(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(["2024", "13"])
        actual = {
            "exit_code": exit_code,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
        }
        expected = {
            "exit_code": 2,
            "stdout": "",
            "stderr": "Error: Invalid month 13: expected an integer between 1 and 12.\n",
        }
        self.assertEqual(actual, expected)
        self.record("cli_invalid_month", ["2024", "13"], expected, actual)

    def test_import_is_safe(self):
        script = (
            "import importlib.util\n"
            "spec = importlib.util.spec_from_file_location("
            "'leap_check', r'"
            + str(REPO_ROOT / "utilities" / "Leap-Year-Calendar" / "main.py")
            + "')\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=False,
            capture_output=True,
            text=True,
        )
        expected = {"exit_code": 0, "stdout": "", "stderr": ""}
        actual = {
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        self.assertEqual(actual, expected)
        self.record("import_safety", {"python": sys.executable}, expected, actual)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(LeapYearCalendarChecks)


if __name__ == "__main__":
    unittest.main()
