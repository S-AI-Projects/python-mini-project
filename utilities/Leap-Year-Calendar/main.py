"""Determine Gregorian leap years and the number of days in a month."""

import sys


MIN_YEAR = 1
MAX_YEAR = 9999

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def is_leap_year(year: int) -> bool:
    """Return True if year is a Gregorian leap year, otherwise False."""
    if isinstance(year, bool) or not isinstance(year, int):
        raise TypeError(
            f"Invalid year type '{type(year).__name__}': "
            "expected an integer between 1 and 9999."
        )
    if year < MIN_YEAR or year > MAX_YEAR:
        raise ValueError(
            f"Invalid year {year}: expected an integer between 1 and 9999."
        )

    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in month of year."""
    if isinstance(year, bool) or not isinstance(year, int):
        raise TypeError(
            f"Invalid year type '{type(year).__name__}': "
            "expected an integer between 1 and 9999."
        )
    if year < MIN_YEAR or year > MAX_YEAR:
        raise ValueError(
            f"Invalid year {year}: expected an integer between 1 and 9999."
        )
    if isinstance(month, bool) or not isinstance(month, int):
        raise TypeError(
            f"Invalid month type '{type(month).__name__}': "
            "expected an integer between 1 and 12."
        )
    if month < 1 or month > 12:
        raise ValueError(
            f"Invalid month {month}: expected an integer between 1 and 12."
        )

    if month == 2:
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def main(argv: list[str] | None = None) -> int:
    """Run the leap-year and days-in-month command-line interface."""
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) not in (1, 2):
        print(
            "Error: Expected a year, or a year followed by a month.",
            file=sys.stderr,
        )
        print(
            "Usage: python3 utilities/Leap-Year-Calendar/main.py "
            "<year> [month]",
            file=sys.stderr,
        )
        return 2

    try:
        year = int(arguments[0])
    except (TypeError, ValueError):
        print(
            f"Error: Invalid year '{arguments[0]}': "
            "expected an integer between 1 and 9999.",
            file=sys.stderr,
        )
        return 2

    if len(arguments) == 1:
        try:
            leap = is_leap_year(year)
        except (TypeError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 2

        print(
            f"{year} is a leap year."
            if leap
            else f"{year} is not a leap year."
        )
        return 0

    try:
        month = int(arguments[1])
    except (TypeError, ValueError):
        print(
            f"Error: Invalid month '{arguments[1]}': "
            "expected an integer between 1 and 12.",
            file=sys.stderr,
        )
        return 2

    try:
        day_count = days_in_month(year, month)
    except (TypeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    print(f"{_MONTH_NAMES[month - 1]} {year} has {day_count} days.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
