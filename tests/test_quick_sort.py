"""Tests for quick_sort in math/Quick-Sort/Quick-Sort.py (R26-T040).

Verifies sorting invariants:
1. Output is ordered ascending (or descending when reverse=True).
2. Input multiplicities (element frequencies) are strictly preserved.
3. Contract: returns a new list; does not mutate the input list.
4. Fixtures: [3, 1, 2], [2, 2, 1], already ordered [1, 2, 3],
   reversed [3, 2, 1], and smallest supported collections ([] and [x]).
"""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Quick-Sort"
    / "Quick-Sort.py"
)


def _load_quick_sort():
    """Load quick_sort from the hypenated path dynamically."""
    spec = importlib.util.spec_from_file_location("quick_sort_module", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quick_sort


@pytest.fixture(scope="module")
def quick_sort():
    return _load_quick_sort()


class TestQuickSortFixtures:
    """Tests using the exact fixtures specified in task R26-T040."""

    def test_unsorted_fixture(self, quick_sort):
        """Fixture [3, 1, 2] -> expected ascending output [1, 2, 3]."""
        inp = [3, 1, 2]
        expected = [1, 2, 3]
        assert quick_sort(inp) == expected

    def test_duplicates_multiplicity_preserved(self, quick_sort):
        """Fixture [2, 2, 1] -> expected ascending output [1, 2, 2].

        Crucial invariant: preserving element multiplicities.
        Catches the plausible one-line mutation: 'value < pivot' instead of 'value <= pivot'.
        """
        inp = [2, 2, 1]
        expected = [1, 2, 2]
        assert quick_sort(inp) == expected

    def test_already_ordered_fixture(self, quick_sort):
        """Fixture [1, 2, 3] -> expected ascending output [1, 2, 3]."""
        inp = [1, 2, 3]
        expected = [1, 2, 3]
        assert quick_sort(inp) == expected

    def test_reversed_fixture(self, quick_sort):
        """Fixture [3, 2, 1] -> expected ascending output [1, 2, 3]."""
        inp = [3, 2, 1]
        expected = [1, 2, 3]
        assert quick_sort(inp) == expected

    def test_smallest_supported_collection_empty(self, quick_sort):
        """Smallest supported collection: empty list -> []."""
        assert quick_sort([]) == []

    def test_smallest_supported_collection_single(self, quick_sort):
        """Smallest non-empty collection: single element [42] -> [42]."""
        assert quick_sort([42]) == [42]


class TestDescendingInterface:
    """Verify descending sorting order when reverse=True."""

    def test_descending_unsorted(self, quick_sort):
        """Fixture [3, 1, 2] with reverse=True -> [3, 2, 1]."""
        assert quick_sort([3, 1, 2], reverse=True) == [3, 2, 1]

    def test_descending_duplicates(self, quick_sort):
        """Fixture [2, 2, 1] with reverse=True -> [2, 2, 1]."""
        assert quick_sort([2, 2, 1], reverse=True) == [2, 2, 1]

    def test_descending_already_ordered(self, quick_sort):
        """Fixture [1, 2, 3] with reverse=True -> [3, 2, 1]."""
        assert quick_sort([1, 2, 3], reverse=True) == [3, 2, 1]

    def test_descending_reversed(self, quick_sort):
        """Fixture [3, 2, 1] with reverse=True -> [3, 2, 1]."""
        assert quick_sort([3, 2, 1], reverse=True) == [3, 2, 1]

    def test_descending_empty(self, quick_sort):
        """Empty list with reverse=True -> []."""
        assert quick_sort([], reverse=True) == []


class TestMutationAndReturnContract:
    """Verify that quick_sort does not mutate its input and returns a new list."""

    def test_input_list_is_not_mutated(self, quick_sort):
        """Input list must remain unmodified after sorting."""
        original = [3, 1, 2]
        caller_copy = list(original)
        result = quick_sort(caller_copy)
        assert caller_copy == original
        assert result == [1, 2, 3]

    def test_returns_new_list_instance(self, quick_sort):
        """Returned list must be a distinct object in memory (not in-place)."""
        inp = [3, 1, 2]
        result = quick_sort(inp)
        assert result is not inp

    def test_empty_list_returns_distinct_copy(self, quick_sort):
        """Even for empty list, return value must be a new list instance."""
        inp = []
        result = quick_sort(inp)
        assert result is not inp


class TestExtendedInvariants:
    """Additional edge cases ensuring sorting correctness across integers."""

    def test_negative_numbers(self, quick_sort):
        assert quick_sort([-5, 0, 10, -2, 3]) == [-5, -2, 0, 3, 10]

    def test_all_identical_elements(self, quick_sort):
        assert quick_sort([7, 7, 7, 7]) == [7, 7, 7, 7]

    def test_large_range(self, quick_sort):
        inp = [100, -50, 25, 0, -100, 50]
        assert quick_sort(inp) == [-100, -50, 0, 25, 50, 100]
