"""Repeatability and input-isolation checks for N-Queens print_board."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "utilities"
    / "N-Queens"
    / "N-Queens.py"
)

# main initializes solutions at N-Queens.py:39, and solve appends copied
# solutions at lines 18-20 before main renders each solution at line 49.
SMALLEST_BOARD = [[1]]
SMALLEST_OUTPUT = "♛\n\n"

ORDINARY_BOARD = [
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 0, 1, 0],
]
ORDINARY_OUTPUT = (
    "⬜ ♛ ⬜ ⬜\n"
    "⬜ ⬜ ⬜ ♛\n"
    "♛ ⬜ ⬜ ⬜\n"
    "⬜ ⬜ ♛ ⬜\n"
    "\n"
)


def _load_n_queens():
    spec = importlib.util.spec_from_file_location("n_queens", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load N-Queens module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def n_queens():
    return _load_n_queens()


def _check_render(n_queens, capsys, name, board, n, expected):
    original_board = [row[:] for row in board]
    actual_return = n_queens.print_board(board, n)
    actual = capsys.readouterr().out
    result = {
        "case": name,
        "source_anchor": "N-Queens.py:1-5, 18-20, 39, 49",
        "input": board,
        "expected": expected,
        "actual": actual,
        "expected_input_after": original_board,
        "actual_input_after": board,
        "expected_return": None,
        "actual_return": actual_return,
    }
    with capsys.disabled():
        print("\nR26_T015_CASE=" + json.dumps(result, ensure_ascii=False))

    assert actual_return is None, (
        f"{name}: expected return None, got {actual_return!r}"
    )
    assert actual == expected, (
        f"{name}: expected output {expected!r}, got {actual!r}"
    )
    assert board == original_board, (
        f"{name}: expected input unchanged {original_board!r}, got {board!r}"
    )


def test_smallest_board_repeats_around_an_ordinary_board(n_queens, capsys):
    _check_render(
        n_queens, capsys, "smallest first run", [row[:] for row in SMALLEST_BOARD],
        1, SMALLEST_OUTPUT,
    )
    _check_render(
        n_queens, capsys, "ordinary board", [row[:] for row in ORDINARY_BOARD],
        4, ORDINARY_OUTPUT,
    )
    _check_render(
        n_queens, capsys, "fresh smallest after ordinary",
        [row[:] for row in SMALLEST_BOARD], 1, SMALLEST_OUTPUT,
    )


def test_ordinary_board_has_literal_rendering(n_queens, capsys):
    _check_render(
        n_queens,
        capsys,
        "ordinary board independent run",
        [row[:] for row in ORDINARY_BOARD],
        4,
        ORDINARY_OUTPUT,
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
