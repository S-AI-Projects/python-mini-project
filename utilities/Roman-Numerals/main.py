"""Roman Numeral Converter with Actionable Error Messages and Failure Safety.

Encodes integers 1..3999 as canonical Roman numerals.
Guarantees caller data and filesystem state remain intact upon failure.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Sequence, Tuple, Union

MIN_ROMAN: int = 1
MAX_ROMAN: int = 3999

# Canonical descending (value, numeral) pairs
_NUMERAL_PAIRS: Tuple[Tuple[int, str], ...] = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


def to_roman(number: int) -> str:
    """Encode an integer in 1..3999 as a canonical Roman numeral string.

    Parameters
    ----------
    number : int
        An integer between 1 and 3999 (inclusive).

    Returns
    -------
    str
        Canonical Roman numeral representation (e.g., 1994 -> 'MCMXCIV').

    Raises
    ------
    TypeError
        If `number` is not an int (or is a bool). Error message specifies
        the received type and value, with actionable guidance.
    ValueError
        If `number` is outside 1..3999 (such as 0, negatives, or >= 4000).
        Error message specifies bounds and reasons.
    """
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError(
            f"Expected integer input in range {MIN_ROMAN}..{MAX_ROMAN}, "
            f"got type {type(number).__name__} ({number!r}). "
            "Action: Convert or pass an integer value (e.g. to_roman(42))."
        )

    if number < MIN_ROMAN or number > MAX_ROMAN:
        if number == 0:
            reason = "Zero has no representation in canonical Roman numerals."
        elif number < 0:
            reason = "Negative integers cannot be expressed as Roman numerals."
        else:
            reason = (
                f"Values >= {MAX_ROMAN + 1} exceed standard Roman numeral range "
                "(would require non-standard vinculum/apostrophus notation)."
            )
        raise ValueError(
            f"Integer {number} is out of bounds [{MIN_ROMAN}..{MAX_ROMAN}]. "
            f"{reason} Action: Supply an integer within {MIN_ROMAN}..{MAX_ROMAN}."
        )

    result_parts: List[str] = []
    remaining = number
    for value, numeral in _NUMERAL_PAIRS:
        while remaining >= value:
            result_parts.append(numeral)
            remaining -= value

    return "".join(result_parts)


def convert_many(numbers: Sequence[int]) -> List[str]:
    """Convert a sequence of integers to Roman numerals failure-safely.

    Validates all inputs and guarantees that the caller's input collection
    remains completely unmodified, even if an element raises an exception.

    Parameters
    ----------
    numbers : Sequence[int]
        Sequence of integer values to convert.

    Returns
    -------
    List[str]
        List of canonical Roman numerals corresponding to `numbers`.

    Raises
    ------
    TypeError, ValueError
        If any element in `numbers` is invalid. The caller's input sequence
        is guaranteed not to be mutated.
    """
    # Pure non-mutating transformation: build new list without modifying input
    results: List[str] = []
    for idx, num in enumerate(numbers):
        try:
            results.append(to_roman(num))
        except (TypeError, ValueError) as err:
            raise type(err)(
                f"Batch conversion failed at index {idx} (value={num!r}): {err}"
            ) from err
    return results


def convert_file(
    source_path: Union[str, Path],
    dest_path: Union[str, Path],
) -> int:
    """Read integers from source_path and write Roman numerals to dest_path.

    Uses an atomic temporary file write to ensure that if any line contains
    invalid data or fails to convert, `dest_path` is left completely intact
    and no partial or corrupted output is written to disk.

    Parameters
    ----------
    source_path : str | Path
        Path to text file containing one integer per line.
    dest_path : str | Path
        Path to target file for resulting Roman numerals.

    Returns
    -------
    int
        Count of successfully converted numerals written.

    Raises
    ------
    FileNotFoundError
        If source_path does not exist.
    ValueError, TypeError
        If any line cannot be converted. `dest_path` is left completely intact.
    """
    src = Path(source_path)
    dst = Path(dest_path)

    if not src.is_file():
        raise FileNotFoundError(
            f"Source file not found: {src}. "
            "Action: Check the file path and ensure it exists before running conversion."
        )

    # Read and parse all input lines first
    lines = src.read_text(encoding="utf-8").splitlines()
    converted_numerals: List[str] = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            val = int(stripped)
        except ValueError as exc:
            raise ValueError(
                f"File '{src}' line {line_num} contains non-integer text '{stripped}'. "
                "Action: Ensure each active line contains a valid decimal integer."
            ) from exc

        try:
            converted_numerals.append(to_roman(val))
        except (ValueError, TypeError) as exc:
            raise type(exc)(
                f"File '{src}' line {line_num} conversion failed: {exc}"
            ) from exc

    # Atomic write pattern: write to temp file in destination directory, then replace
    dst_dir = dst.parent if dst.parent.as_posix() != "" else Path(".")
    dst_dir.mkdir(parents=True, exist_ok=True)

    temp_fd, temp_path_str = tempfile.mkstemp(
        dir=str(dst_dir), prefix=".roman_tmp_", text=True
    )
    temp_path = Path(temp_path_str)

    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as temp_file:
            for num in converted_numerals:
                temp_file.write(f"{num}\n")
        # Atomic rename replacing destination
        temp_path.replace(dst)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

    return len(converted_numerals)


def main(argv: Sequence[str] = None) -> int:
    """Command-line interface for Roman Numeral conversion.

    Parameters
    ----------
    argv : Sequence[str], optional
        Command line arguments. Defaults to sys.argv[1:].

    Returns
    -------
    int
        0 on success, non-zero on error.
    """
    parser = argparse.ArgumentParser(
        prog="roman_numerals",
        description="Encode integers 1..3999 as canonical Roman numerals.",
    )
    parser.add_argument(
        "numbers",
        nargs="*",
        type=int,
        help="One or more integers between 1 and 3999 to convert.",
    )
    parser.add_argument(
        "--file",
        "-f",
        dest="file",
        help="Input file with one integer per line to convert.",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        help="Output file path (used with --file).",
    )

    args = parser.parse_args(argv)

    if args.file:
        dest = args.output or f"{args.file}.roman.txt"
        try:
            count = convert_file(args.file, dest)
            print(f"Successfully converted {count} numbers to '{dest}'.")
            return 0
        except Exception as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1

    if args.numbers:
        for num in args.numbers:
            try:
                print(to_roman(num))
            except Exception as err:
                print(f"Error converting {num}: {err}", file=sys.stderr)
                return 1
        return 0

    # Interactive mode if no arguments provided
    print("Roman Numeral Converter (1..3999). Type 'quit' or 'exit' to stop.")
    while True:
        try:
            raw = input("Enter integer: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if raw.lower() in ("quit", "exit", "q"):
            break
        if not raw:
            continue
        try:
            val = int(raw)
            print(f"{val} -> {to_roman(val)}")
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
