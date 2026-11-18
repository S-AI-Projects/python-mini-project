# Leap Year Calendar

A standard-library Python utility that checks whether a year is a Gregorian
leap year and reports the number of days in a month.

## Supported Limits

- Years: `1` through `9999`
- Months: `1` through `12`
- Boolean values, non-integer values, and out-of-range values are rejected.

The Gregorian leap-year rule is used: divisible by 4, except divisible by 100
unless also divisible by 400.

## Run

From the repository root:

```bash
python3 utilities/Leap-Year-Calendar/main.py 2000
```

Or check a month:

```bash
python3 utilities/Leap-Year-Calendar/main.py 2024 2
```

## Input and Output Examples

Leap-year check:

```text
$ python3 utilities/Leap-Year-Calendar/main.py 2000
2000 is a leap year.
```

```text
$ python3 utilities/Leap-Year-Calendar/main.py 1900
1900 is not a leap year.
```

Days-in-month check:

```text
$ python3 utilities/Leap-Year-Calendar/main.py 2024 2
February 2024 has 29 days.
```

```text
$ python3 utilities/Leap-Year-Calendar/main.py 2023 2
February 2023 has 28 days.
```

Invalid input:

```text
$ python3 utilities/Leap-Year-Calendar/main.py 2024 13
Error: Invalid month 13: expected an integer between 1 and 12.
```

Invalid input exits with status code `2`; successful checks exit with `0`.

## Importable Functions

`main.py` exposes `is_leap_year(year)` and `days_in_month(year, month)`.
Because the folder name contains hyphens, import it by file path in Python
applications or run the CLI command shown above.
