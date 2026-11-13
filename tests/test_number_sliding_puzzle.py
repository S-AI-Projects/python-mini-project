"""
Tests for games/Number-Sliding-Puzzle/Number-Sliding-Puzzle.py

Focus areas:
- Regression test for "8-Puzzle solvability check can allow impossible
  puzzles" (issue #1822): is_solvable() must depend only on inversion
  parity for this 3x3 board, not on the blank tile's row.
- A ground-truth oracle built independently via breadth-first search over
  every reachable board state, so the tests validate is_solvable() against
  actual reachability rather than re-deriving the same formula.

The module file uses hyphens in its name, so it's loaded via importlib
rather than a normal `import` statement. The game module also imports
`utils.validation`, so a lightweight stub is installed for that before
import.
"""

import importlib.util
import itertools
import json
import sys
import types
from collections import deque
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Number-Sliding-Puzzle"
    / "Number-Sliding-Puzzle.py"
)

# These contract cases use the 3x3 tile permutation initialized at
# Number-Sliding-Puzzle.py:51 and passed to is_solvable before reshaping at
# lines 54 and 57-61. Expected parity is calculated from each literal list,
# not by calling is_solvable.
IS_SOLVABLE_CONTRACT_CASES = [
    {
        "name": "smallest valid board and minimum inversion boundary",
        "source_anchor": "Number-Sliding-Puzzle.py:11-17, 21-27, 41-42, 51, 54",
        "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 0],
        "inversions": 0,
        "calculation": "The non-blank tiles are ascending: 0 inversions is even.",
        "expected": True,
    },
    {
        "name": "ordinary board",
        "source_anchor": "Number-Sliding-Puzzle.py:11-17, 41-42, 51-54",
        "numbers": [1, 2, 3, 4, 5, 6, 0, 7, 8],
        "inversions": 0,
        "calculation": "Excluding 0 leaves ascending tiles: 0 inversions is even.",
        "expected": True,
    },
    {
        "name": "minimum odd inversion boundary",
        "source_anchor": "Number-Sliding-Puzzle.py:14-17, 21-27, 33-42, 51",
        "numbers": [2, 1, 3, 4, 5, 6, 7, 8, 0],
        "inversions": 1,
        "calculation": "Only 2-before-1 is inverted: 1 inversion is odd.",
        "expected": False,
    },
    {
        "name": "maximum inversion boundary",
        "source_anchor": "Number-Sliding-Puzzle.py:14-17, 21-27, 33-42, 51",
        "numbers": [8, 7, 6, 5, 4, 3, 2, 1, 0],
        "inversions": 28,
        "calculation": "The 8 numbered tiles are reversed: 8*7/2 = 28, even.",
        "expected": True,
    },
]


def _install_utils_validation_stub():
    """The game module does `from utils.validation import get_int, get_yes_no`.
    Provide a minimal stub so the module can be imported in isolation,
    without needing the rest of the repository present."""
    utils_pkg = types.ModuleType("utils")
    validation_mod = types.ModuleType("utils.validation")
    validation_mod.get_int = lambda *a, **k: 0
    validation_mod.get_yes_no = lambda *a, **k: False
    utils_pkg.validation = validation_mod
    sys.modules["utils"] = utils_pkg
    sys.modules["utils.validation"] = validation_mod


@pytest.fixture(scope="module")
def puzzle_module():
    _install_utils_validation_stub()
    spec = importlib.util.spec_from_file_location("number_sliding_puzzle", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["number_sliding_puzzle"] = module
    spec.loader.exec_module(module)
    return module


# ── Ground-truth oracle: BFS over every reachable 3x3 sliding-puzzle state ──

def _neighbors(state):
    idx = state.index(0)
    r, c = divmod(idx, 3)
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            nidx = nr * 3 + nc
            lst = list(state)
            lst[idx], lst[nidx] = lst[nidx], lst[idx]
            yield tuple(lst)


@pytest.fixture(scope="module")
def reachable_states():
    """All board states reachable from the goal state via legal slides.
    This is the ground truth for "solvable" - it does not use is_solvable()
    at all, so comparing against it is a genuine independent check."""
    goal = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    visited = {goal}
    queue = deque([goal])
    while queue:
        state = queue.popleft()
        for nxt in _neighbors(state):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return visited


def test_oracle_finds_exactly_half_of_all_permutations(reachable_states):
    # Sanity check on the oracle itself: exactly half of all 9! permutations
    # of a 3x3 board are reachable from the goal state.
    assert len(reachable_states) == 181440


def test_is_solvable_matches_bfs_reachability_for_all_states(puzzle_module, reachable_states):
    """
    The definitive regression test for issue #1822: for EVERY one of the
    362,880 possible board permutations, is_solvable() must agree with
    whether that state is actually reachable (solvable) from the goal,
    regardless of which row the blank tile sits on.
    """
    mismatches = []
    for perm in itertools.permutations(range(9)):
        expected = perm in reachable_states
        actual = puzzle_module.is_solvable(list(perm))
        if actual != expected:
            mismatches.append(perm)

    assert not mismatches, (
        f"is_solvable() disagreed with BFS reachability on {len(mismatches)} "
        f"states, e.g. {mismatches[:5]}"
    )


# ── Targeted examples (including the specific blank-row bug scenario) ──────

def test_goal_state_is_solvable(puzzle_module):
    assert puzzle_module.is_solvable([1, 2, 3, 4, 5, 6, 7, 8, 0]) is True


def test_single_adjacent_swap_is_unsolvable(puzzle_module):
    # Classic example: swapping any two tiles in the goal state (1 inversion)
    # always produces an unsolvable board.
    assert puzzle_module.is_solvable([2, 1, 3, 4, 5, 6, 7, 8, 0]) is False


def test_solvable_state_with_blank_in_middle_row(puzzle_module):
    """
    This is the exact scenario the old buggy formula got wrong: zero
    inversions among the numbered tiles, but with the blank tile in the
    middle row. The old code incorrectly reported this as unsolvable.
    """
    assert puzzle_module.is_solvable([1, 2, 3, 0, 4, 5, 6, 7, 8]) is True


def test_unsolvable_state_with_blank_in_middle_row(puzzle_module):
    """
    The mirror-image bug case: one inversion (unsolvable) but with the
    blank in the middle row. The old code incorrectly reported this as
    solvable.
    """
    assert puzzle_module.is_solvable([2, 1, 3, 0, 4, 5, 6, 7, 8]) is False


def test_solvability_is_independent_of_blank_position(puzzle_module):
    """For a fixed relative ordering of the numbered tiles (same inversion
    count), solvability must not change no matter which cell the blank
    tile is moved into."""
    numbered_tiles = [1, 2, 3, 4, 5, 6, 7, 8]  # 0 inversions
    results = set()
    for blank_pos in range(9):
        state = numbered_tiles[:blank_pos] + [0] + numbered_tiles[blank_pos:]
        results.add(puzzle_module.is_solvable(state))
    assert results == {True}


def test_shuffle_loop_never_yields_unsolvable_state(puzzle_module, reachable_states):
    """Simulates the shuffle loop from main(): every state it accepts must
    actually be a reachable (solvable) state."""
    import random

    random.seed(42)
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    for _ in range(200):
        random.shuffle(numbers)
        if puzzle_module.is_solvable(numbers) and numbers != [1, 2, 3, 4, 5, 6, 7, 8, 0]:
            assert tuple(numbers) in reachable_states


@pytest.mark.parametrize(
    "case",
    IS_SOLVABLE_CONTRACT_CASES,
    ids=[case["name"] for case in IS_SOLVABLE_CONTRACT_CASES],
)
def test_is_solvable_contract_boundaries(puzzle_module, case):
    numbers = case["numbers"][:]
    original_numbers = numbers[:]
    expected = case["expected"]
    actual = puzzle_module.is_solvable(numbers)

    print(
        "R26_T012_CASE="
        + json.dumps(
            {
                "case": case["name"],
                "source_anchor": case["source_anchor"],
                "input": original_numbers,
                "input_after": numbers,
                "inversions": case["inversions"],
                "calculation": case["calculation"],
                "expected": expected,
                "actual": actual,
            }
        )
    )
    assert actual is expected, (
        f"{case['name']}: expected {expected!r}, got {actual!r}; "
        f"input={original_numbers!r}, inversions={case['inversions']}"
    )
    assert numbers == original_numbers, (
        f"{case['name']}: expected input unchanged {original_numbers!r}, "
        f"got {numbers!r}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))