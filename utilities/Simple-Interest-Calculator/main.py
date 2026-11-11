"""💰 Simple Interest Calculator
Calculate simple interest accurately using decimal arithmetic.
"""

from decimal import Decimal, InvalidOperation
import sys
from typing import Any


def to_decimal(value: Any) -> Decimal:
    """Convert input to a finite Decimal.

    Rejects booleans, non-numeric strings, NaN, Infinity, and unsupported types.
    Floats are converted via Decimal(str(x)) to preserve decimal precision.
    """
    if isinstance(value, bool):
        raise TypeError("Booleans are not supported as numeric inputs")

    if not isinstance(value, (int, float, str, Decimal)):
        raise TypeError(f"Unsupported input type: {type(value).__name__}")

    if isinstance(value, float):
        d_val = Decimal(str(value))
    elif isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Empty string cannot be converted to a number")
        try:
            d_val = Decimal(cleaned)
        except InvalidOperation as err:
            raise ValueError(f"Invalid numeric string: {value!r}") from err
    else:
        try:
            d_val = Decimal(value)
        except InvalidOperation as err:
            raise ValueError(f"Invalid numeric value: {value!r}") from err

    if not d_val.is_finite():
        raise ValueError("Non-finite numbers (NaN, Infinity) are not supported")

    return d_val


def calculate_simple_interest(principal: Any, rate: Any, years: Any) -> Decimal:
    """Calculate simple interest using formula: (principal * rate * years) / 100.

    Computed strictly using decimal.Decimal arithmetic.
    Negative principal raises ValueError.
    Negative rate and negative years are not restricted by the contract.
    """
    p = to_decimal(principal)
    r = to_decimal(rate)
    t = to_decimal(years)

    if p < Decimal("0"):
        raise ValueError("Principal cannot be negative")

    return (p * r * t) / Decimal("100")


def format_currency(amount: Decimal) -> str:
    """Format Decimal amount to a standard string without scientific notation."""
    if not isinstance(amount, Decimal):
        raise TypeError("amount must be a Decimal")
    return f"{amount:f}"


def main() -> None:
    """CLI entry point supporting argument mode and interactive mode."""
    if len(sys.argv) > 1:
        if len(sys.argv) != 4:
            sys.stderr.write(
                "❌ Error: Exactly 3 arguments required: <principal> <rate> <years>\n"
            )
            sys.exit(1)

        try:
            interest = calculate_simple_interest(
                sys.argv[1], sys.argv[2], sys.argv[3]
            )
            print(f"💰 Simple Interest: {format_currency(interest)}")
        except (ValueError, TypeError) as err:
            sys.stderr.write(f"❌ Error: {err}\n")
            sys.exit(1)
    else:
        print("💰 Simple Interest Calculator 💰")
        print("Calculate simple interest accurately using decimal arithmetic.\n")
        try:
            p_in = input("🎯 Enter Principal amount: ")
            r_in = input("📊 Enter Annual Interest Rate (%): ")
            t_in = input("⏳ Enter Time period (years): ")
            interest = calculate_simple_interest(p_in, r_in, t_in)
            print(f"\n✅ Simple Interest: {format_currency(interest)}")
            print("👋 Thanks for using Simple Interest Calculator!\n")
        except (ValueError, TypeError) as err:
            sys.stderr.write(f"\n❌ Error: {err}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
