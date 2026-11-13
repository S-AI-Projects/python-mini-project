"""Reference-comparison tests for Reverse Hangman's sequence reversal helper."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "games"
    / "Reverse-Hangman-Game"
    / "Reverse-Hangman-Game.py"
)

# Explicit expected values are independent of the implementation. Strings
# reverse Unicode code points; bytes reverse individual byte values.
REVERSAL_CASES = [
    ("empty string", "", "", 0),
    ("singleton string", "A", "A", 1),
    ("three-code-point string", "ABC", "CBA", 3),
    ("two-code-point string", "ab", "ba", 2),
    ("repeated-code-point string", "level", "level", 5),
    ("unicode code points", "Aé🙂", "🙂éA", 3),
    ("empty bytes", b"", b"", 0),
    ("singleton bytes", b"A", b"A", 1),
    ("three-byte sequence", b"ABC", b"CBA", 3),
    ("two-byte sequence", b"\x00\xff", b"\xff\x00", 2),
    ("UTF-8 bytes reverse as bytes", b"\xc3\xa9", b"\xa9\xc3", 2),
    ("three binary bytes", b"\x00\x7f\xff", b"\xff\x7f\x00", 3),
    ("empty list", [], [], 0),
    ("singleton list", ["A"], ["A"], 1),
    ("three-element list", ["A", "B", "C"], ["C", "B", "A"], 3),
    ("two-element list", [1, 2], [2, 1], 2),
    ("repeated list values", [1, 1, 2], [2, 1, 1], 3),
    ("empty tuple", (), (), 0),
    ("singleton tuple", ("A",), ("A",), 1),
    ("three-element tuple", ("A", "B", "C"), ("C", "B", "A"), 3),
    ("two-element tuple", (1, 2), (2, 1), 2),
    ("repeated tuple values", (1, 1, 2), (2, 1, 1), 3),
    ("singleton integer list", [0], [0], 1),
    ("mixed list", ["A", 2, None], [None, 2, "A"], 3),
]

CASE_RESULTS = []


def _load_module():
    spec = importlib.util.spec_from_file_location("reverse_hangman_game", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Reverse Hangman module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _reference_reverse(value):
    """Reverse by pairwise swaps, independently of slicing/reversed()."""
    items = list(value)
    left = 0
    right = len(items) - 1
    while left < right:
        items[left], items[right] = items[right], items[left]
        left += 1
        right -= 1

    if isinstance(value, str):
        return "".join(items)
    if isinstance(value, bytes):
        return bytes(items)
    if isinstance(value, tuple):
        return tuple(items)
    return items


def _evidence_value(value):
    if isinstance(value, bytes):
        return {"type": "bytes", "hex": value.hex()}
    if isinstance(value, tuple):
        return {"type": "tuple", "items": list(value)}
    if isinstance(value, list):
        return {"type": "list", "items": value}
    return {"type": "str", "value": value}


@pytest.fixture(scope="module")
def game_module():
    return _load_module()


@pytest.mark.parametrize(
    "name,value,expected,expected_length",
    REVERSAL_CASES,
    ids=[case[0] for case in REVERSAL_CASES],
)
def test_reverse_value_matches_explicit_table_and_reference(
    game_module, name, value, expected, expected_length
):
    original = value[:] if isinstance(value, (str, bytes, list, tuple)) else value
    reference = _reference_reverse(value)
    actual = game_module.reverse_value(value)
    reversed_twice = game_module.reverse_value(actual)
    result = {
        "case": name,
        "input": _evidence_value(value),
        "expected": _evidence_value(expected),
        "reference": _evidence_value(reference),
        "actual": _evidence_value(actual),
        "expected_twice": _evidence_value(value),
        "actual_twice": _evidence_value(reversed_twice),
        "expected_length": expected_length,
        "actual_length": len(actual),
        "input_after": _evidence_value(value),
        "source_anchor": "Reverse-Hangman-Game.py:11-19 (standalone helper)",
    }
    CASE_RESULTS.append(result)
    print("R26_T013_CASE=" + json.dumps(result, ensure_ascii=False))

    assert reference == expected, (
        f"{name}: independent oracle expected {expected!r}, got {reference!r}"
    )
    assert actual == expected, f"{name}: expected {expected!r}, got {actual!r}"
    assert len(actual) == expected_length, (
        f"{name}: expected length {expected_length}, got {len(actual)}"
    )
    assert reversed_twice == value, (
        f"{name}: reversing twice should restore {value!r}, "
        f"got {reversed_twice!r}"
    )
    assert len(reversed_twice) == expected_length, (
        f"{name}: expected twice-reversed length {expected_length}, "
        f"got {len(reversed_twice)}"
    )
    assert type(actual) is type(value), (
        f"{name}: expected result type {type(value).__name__}, "
        f"got {type(actual).__name__}"
    )
    assert value == original, (
        f"{name}: expected input unchanged {original!r}, got {value!r}"
    )


def test_contract_covers_at_least_twenty_small_values():
    expected_count = 20
    actual_count = len(REVERSAL_CASES)
    assert actual_count >= expected_count, (
        f"expected at least {expected_count} cases, got {actual_count}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
