"""
Password Strength Meter

An educational checklist evaluator that checks a password against four basic
structural criteria:
1. Length >= 12 characters
2. Mixed letter case (at least one uppercase AND at least one lowercase letter)
3. Contains a digit (defined strictly via str.isdecimal, matching standard decimal
   digits '0'-'9' and excluding superscript numbers like '²')
4. Contains a symbol (defined strictly as characters in string.punctuation;
   whitespace is NOT considered a symbol)

Invariants maintained:
- Invariant A: 0 <= count_satisfied <= 4, and count_satisfied == sum(bool(c) for c in results.values()).
- Invariant B: check_password("") evaluates every condition to False and has count 0.
- Invariant C (Monotonicity): Appending any character to a string never turns a
  satisfied condition into an unsatisfied one.
- Invariant D (Order Independence): Shuffling the characters of a string does not
  change the result of any condition or the count.
- Invariant E (Length Boundary): Lengths 0, 1, 11 fail the length check; lengths
  12 and 13 pass.

IMPORTANT:
This module is strictly an educational rule checklist and is NOT a calibrated
security-strength estimate.
"""

from __future__ import annotations

import getpass
import string
import sys

DISCLAIMER: str = (
    "DISCLAIMER: This checklist evaluates basic structural rules and is NOT "
    "a calibrated security-strength estimate. It does not measure entropy, "
    "crack resistance, or vulnerability to dictionary or breach attacks."
)

CHECK_LABELS: dict[str, str] = {
    "length": "Length >= 12 characters",
    "mixed_case": "Mixed case letters (uppercase and lowercase)",
    "digit": "Decimal digit (0-9 via str.isdecimal)",
    "symbol": "Punctuation symbol (in string.punctuation)",
}


def check_password(password: str) -> dict[str, bool]:
    """
    Evaluate the given password against the 4-point educational checklist.

    Args:
        password: The input string to check.

    Returns:
        A dictionary mapping each condition name to a boolean indicating
        whether the criterion was met.

    Raises:
        TypeError: If password is not a string.
    """
    if not isinstance(password, str):
        raise TypeError(f"password must be a string, got {type(password).__name__}")

    return {
        "length": len(password) >= 12,
        "mixed_case": any(c.isupper() for c in password) and any(c.islower() for c in password),
        "digit": any(c.isdecimal() for c in password),
        "symbol": any(c in string.punctuation for c in password),
    }


def count_satisfied(results: dict[str, bool]) -> int:
    """
    Return the total number of satisfied checklist conditions.

    Args:
        results: Dictionary mapping condition names to booleans.

    Returns:
        Integer count between 0 and 4.
    """
    return sum(1 for satisfied in results.values() if satisfied)


def format_report(results: dict[str, bool], count: int | None = None) -> str:
    """
    Format evaluation results into a human-readable checklist report.

    Args:
        results: Dictionary mapping condition names to booleans.
        count: Optional pre-computed count of satisfied checks.

    Returns:
        Formatted string report including the mandatory disclaimer.
    """
    if count is None:
        count = count_satisfied(results)

    lines: list[str] = [
        "🛡️ Password Strength Checklist Evaluation 🛡️",
        "----------------------------------------",
    ]

    for key, label in CHECK_LABELS.items():
        status = "✅ PASS" if results.get(key, False) else "❌ FAIL"
        lines.append(f"  {status} : {label}")

    lines.append("----------------------------------------")
    lines.append(f"Criteria Satisfied: {count}/4")
    lines.append("")
    lines.append(DISCLAIMER)

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point.

    Interactive mode (0 arguments): prompts for password using getpass so
    input is not echoed to the terminal.
    Test mode (1 argument): evaluates the provided argument.
    Invalid usage (>1 argument): prints error and exits with code 2.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 on success, non-zero on failure).
    """
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) == 0:
        print("🛡️ Password Strength Meter 🛡️")
        try:
            password = getpass.getpass("🔑 Enter password to evaluate: ")
        except (KeyboardInterrupt, EOFError):
            print("\nEvaluation cancelled.")
            return 1
    elif len(argv) == 1:
        if argv[0] in ("-h", "--help"):
            print("Usage: python3 main.py [PASSWORD]")
            print()
            print("Evaluate password complexity against an educational 4-point checklist.")
            print()
            print("WARNING: Providing a password via command-line arguments can expose it")
            print("in shell history files and system process lists.")
            return 0
        password = argv[0]
    else:
        sys.stderr.write("❌ Error: Expected at most one password argument.\n")
        sys.stderr.write("Usage: python3 main.py [PASSWORD]\n")
        return 2

    results = check_password(password)
    report = format_report(results)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
