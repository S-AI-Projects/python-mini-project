import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "utilities"
    / "Leap-Year-Calendar"
    / "main.py"
)
SPEC = importlib.util.spec_from_file_location("leap_year_calendar", MODULE_PATH)
leap_year_calendar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(leap_year_calendar)


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (1900, False),
        (2000, True),
        (2023, False),
        (2024, True),
    ],
)
def test_is_leap_year(year, expected):
    assert leap_year_calendar.is_leap_year(year) is expected


def test_days_in_month():
    assert leap_year_calendar.days_in_month(2024, 2) == 29
    assert leap_year_calendar.days_in_month(2023, 2) == 28
    assert leap_year_calendar.days_in_month(2024, 4) == 30
    assert leap_year_calendar.days_in_month(2024, 1) == 31


def test_validation_errors_are_actionable():
    with pytest.raises(
        TypeError,
        match=(
            r"Invalid year type 'bool': expected an integer "
            r"between 1 and 9999"
        ),
    ):
        leap_year_calendar.is_leap_year(True)

    with pytest.raises(
        ValueError,
        match=r"Invalid year 0: expected an integer between 1 and 9999",
    ):
        leap_year_calendar.is_leap_year(0)

    with pytest.raises(
        ValueError,
        match=r"Invalid month 13: expected an integer between 1 and 12",
    ):
        leap_year_calendar.days_in_month(2024, 13)


def test_failed_calls_leave_caller_data_unchanged(tmp_path):
    caller_data = {"year": 2024, "month": 13, "records": [1, 2, 3]}
    original_data = {
        "year": caller_data["year"],
        "month": caller_data["month"],
        "records": caller_data["records"].copy(),
    }

    file_path = tmp_path / "calendar.txt"
    file_path.write_text("unchanged", encoding="utf-8")
    original_bytes = file_path.read_bytes()

    with pytest.raises(ValueError):
        leap_year_calendar.days_in_month(
            caller_data["year"],
            caller_data["month"],
        )

    assert caller_data == original_data
    assert file_path.read_bytes() == original_bytes


def test_main_reports_invalid_month(capsys):
    exit_code = leap_year_calendar.main(["2024", "13"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert captured.err == (
        "Error: Invalid month 13: expected an integer between 1 and 12.\n"
    )


def test_main_reports_invalid_arguments(capsys):
    exit_code = leap_year_calendar.main([])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Usage:" in captured.err
    assert "year" in captured.err
