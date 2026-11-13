"""Contract checks for binary_search found and absent-result paths."""

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "math"
    / "Binary-Search"
    / "Binary-Search.py"
)

# The supported empty-list state is defined by high = len(arr) - 1 at source
# line 17; the loop at line 19 is skipped and the miss sentinel is line 30.
ORDINARY_INPUT = [2, 4, 6, 8]
ORDINARY_EXPECTED = {2: 0, 8: 3, 5: -1}
SINGLETON_INPUT = [7]
SINGLETON_EXPECTED = {7: 0, 3: -1}
EMPTY_INPUT = []
EMPTY_EXPECTED = -1


def _load_binary_search():
    spec = importlib.util.spec_from_file_location("binary_search_module", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load binary search module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def binary_search_module():
    return _load_binary_search()


def _assert_search(module, values, target, expected, case):
    original = values.copy()
    actual = module.binary_search(values, target)
    result = {
        "case": case,
        "source_anchor": (
            "binary_search at Binary-Search.py:11; high=len(arr)-1 at line "
            "17; loop condition at line 19; miss sentinel at line 30; "
            "duplicate equality return at lines 23-24"
        ),
        "input": values,
        "target": target,
        "expected": expected,
        "actual": actual,
        "expected_input_after": original,
        "actual_input_after": values,
    }
    print("R26_T018_CASE=" + json.dumps(result))

    assert actual == expected, (
        f"{case}: expected index {expected}, got {actual}"
    )
    assert values == original, (
        f"{case}: expected input unchanged {original!r}, got {values!r}"
    )


@pytest.mark.parametrize(
    ("target", "expected"),
    [(2, 0), (8, 3), (5, -1)],
)
def test_ordinary_search_contract(binary_search_module, target, expected):
    _assert_search(
        binary_search_module,
        ORDINARY_INPUT.copy(),
        target,
        expected,
        f"ordinary list target {target}",
    )


@pytest.mark.parametrize(("target", "expected"), [(7, 0), (3, -1)])
def test_singleton_search_contract(binary_search_module, target, expected):
    _assert_search(
        binary_search_module,
        SINGLETON_INPUT.copy(),
        target,
        expected,
        f"singleton target {target}",
    )


def test_empty_list_returns_miss_sentinel_then_search_still_succeeds(
    binary_search_module,
):
    _assert_search(
        binary_search_module,
        EMPTY_INPUT.copy(),
        2,
        EMPTY_EXPECTED,
        "empty collection absent-result branch",
    )
    _assert_search(
        binary_search_module,
        ORDINARY_INPUT.copy(),
        8,
        3,
        "ordinary search succeeds after empty miss",
    )


def test_duplicate_values_return_a_matching_index(binary_search_module):
    values = [2, 4, 4, 4, 8]
    actual = binary_search_module.binary_search(values, 4)
    result = {
        "case": "duplicate values return any matching index",
        "source_anchor": "Binary-Search.py:23-24 returns immediately on equality",
        "input": values,
        "target": 4,
        "expected_matching_indices": [1, 2, 3],
        "actual": actual,
    }
    print("R26_T018_CASE=" + json.dumps(result))

    assert actual in result["expected_matching_indices"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
