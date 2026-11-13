"""Calculate and split a tip-inclusive bill using Decimal currency amounts."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CENT = Decimal("0.01")


def _as_decimal(value, name):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not amount.is_finite():
        raise ValueError(f"{name} must be a finite number")
    return amount


def calculate_split(bill, tip_percent, people):
    """Return rounded currency shares whose sum is the rounded tipped total."""
    bill_amount = _as_decimal(bill, "bill")
    tip_rate = _as_decimal(tip_percent, "tip_percent")
    if bill_amount < 0:
        raise ValueError("bill must not be negative")
    if tip_rate < 0:
        raise ValueError("tip_percent must not be negative")
    if isinstance(people, bool) or not isinstance(people, int) or people <= 0:
        raise ValueError("people must be a positive integer")

    total = (bill_amount * (Decimal("1") + tip_rate / Decimal("100"))).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    cents = int(total * 100)
    base_share, extra_cents = divmod(cents, people)
    return [
        Decimal(base_share + (1 if index < extra_cents else 0)) / 100
        for index in range(people)
    ]


def main():
    print("💵 TIP CALCULATOR 💵")
    try:
        bill = input("Bill amount: ")
        tip_percent = input("Tip percentage: ")
        people = int(input("Number of people: "))
        shares = calculate_split(bill, tip_percent, people)
    except (ValueError, ArithmeticError) as exc:
        print(f"Invalid input: {exc}")
        return

    total = sum(shares, Decimal("0.00"))
    print("Shares: " + ", ".join(f"${share:.2f}" for share in shares))
    print(f"Total: ${total:.2f}")


if __name__ == "__main__":
    main()
