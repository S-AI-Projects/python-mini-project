# Tip Calculator

Calculate a bill total after a percentage tip, then split that rounded total
into currency shares. Any extra cent is assigned to the first shares, so the
shares always sum exactly to the rounded total.

## Run

From the repository root:

```bash
python3 utilities/Tip-Calculator/main.py
```

The CLI asks for the bill amount, tip percentage, and number of people.

## Runnable example

This example is executed and its exact output checked by `test_main.py`:

```python example
from decimal import Decimal

from main import calculate_split

shares = calculate_split(Decimal("100.00"), Decimal("10"), 3)
print("Shares: " + ", ".join(f"${share:.2f}" for share in shares))
print(f"Total: ${sum(shares):.2f}")
```

Output:

```text
Shares: $36.67, $36.67, $36.66
Total: $110.00
```

## Contract and supported limits

- `calculate_split(bill, tip_percent, people)` accepts non-negative monetary
  amounts and tip percentages, plus a positive integer number of people.
- Currency totals are rounded to two decimal places using half-up rounding
  before splitting.
- The result is a list of `Decimal` currency shares in person order. Each share
  has two decimal places and their sum equals the rounded bill-plus-tip total.
- A non-positive or non-integer `people` value, negative amount, or invalid
  or non-finite number raises `ValueError`.
- There is no configured maximum amount, tip percentage, or number of people;
  calculations are subject to Python's active `Decimal` precision and
  available memory.

For the documented example, bill `100.00`, tip `10%`, and `3` people produce a
total of `110.00` and shares `36.67`, `36.67`, and `36.66`. A people count of
`0` is rejected with `ValueError`.

Run the focused tests from the repository root:

```bash
python3 -m unittest discover -s utilities/Tip-Calculator -p "test_*.py"
```
