"""Contract and deterministic property checks for affected Dots & Boxes."""

import importlib.util
import json
import os
import random
from pathlib import Path

import pytest


MODULE_PATH = Path(os.environ.get(
    "DOTS_BOXES_SOURCE",
    Path(__file__).resolve().parents[1]
    / "games"
    / "Dots-Boxes-AI"
    / "Dots-Boxes-AI.py",
))

# The game accepts board sizes 2..8 at Dots-Boxes-AI.py:76-80 and validates
# edge coordinates at lines 151-162 after converting row/col at line 149.
SMALL_CASES = [
    {
        "name": "smallest horizontal top edge",
        "source_anchor": "Dots-Boxes-AI.py:14-21, 76-80, 149-153",
        "args": ("h", 0, 0, 2),
        "expected": [(0, 0)],
    },
    {
        "name": "ordinary horizontal interior edge",
        "source_anchor": "Dots-Boxes-AI.py:14-26, 76-80, 149-153",
        "args": ("h", 1, 0, 2),
        "expected": [(0, 0), (1, 0)],
    },
]
PROPERTY_SEED = 26014
PROPERTY_CASE_COUNT = 128


def _load_module():
    spec = importlib.util.spec_from_file_location("dots_boxes_ai", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Dots & Boxes module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _reference_affected_boxes(direction, row, col, size):
    """Scan valid boxes and select those touching the requested edge."""
    affected = []
    for box_row in range(size):
        for box_col in range(size):
            if direction == "h":
                touches = box_col == col and box_row in (row - 1, row)
            else:
                touches = box_row == row and box_col in (col - 1, col)
            if touches:
                affected.append((box_row, box_col))
    return affected


def _verify_result(module, args, expected):
    original_args = args
    actual = module.get_affected_boxes(*args)
    repeated = module.get_affected_boxes(*tuple(original_args))

    assert type(actual) is list, f"expected list, got {type(actual).__name__}"
    assert all(
        type(box) is tuple
        and len(box) == 2
        and all(type(index) is int for index in box)
        for box in actual
    ), f"expected list of integer coordinate pairs, got {actual!r}"
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert repeated == expected, (
        f"fresh equivalent input: expected {expected!r}, got {repeated!r}"
    )
    assert repeated is not actual, "each call should return a fresh list"
    actual.append((-1, -1))
    assert repeated == expected, (
        f"mutating one result changed an independent result: {repeated!r}"
    )
    assert args == original_args, (
        f"expected input values unchanged {original_args!r}, got {args!r}"
    )
    return repeated


@pytest.fixture(scope="module")
def dots_boxes():
    return _load_module()


@pytest.mark.parametrize(
    "case",
    SMALL_CASES,
    ids=[case["name"] for case in SMALL_CASES],
)
def test_small_valid_inputs_have_explicit_results(dots_boxes, case):
    args = case["args"]
    expected = case["expected"]
    actual = dots_boxes.get_affected_boxes(*args)
    reference = _reference_affected_boxes(*args)
    print(
        "R26_T014_CASE="
        + json.dumps(
            {
                "case": case["name"],
                "source_anchor": case["source_anchor"],
                "input": args,
                "expected": expected,
                "reference": reference,
                "actual": actual,
            }
        )
    )

    assert reference == expected, (
        f"{case['name']}: expected reference {expected!r}, got {reference!r}"
    )
    _verify_result(dots_boxes, args, expected)


def test_fixed_seed_valid_cases_match_box_scan_reference(dots_boxes):
    rng = random.Random(PROPERTY_SEED)
    results = []
    for case_number in range(PROPERTY_CASE_COUNT):
        size = rng.randint(2, 8)
        direction = rng.choice(("h", "v"))
        row = rng.randint(0, size if direction == "h" else size - 1)
        col = rng.randint(0, size - 1 if direction == "h" else size)
        args = (direction, row, col, size)
        expected = _reference_affected_boxes(*args)
        actual = dots_boxes.get_affected_boxes(*args)
        result = {
            "case": f"seed-{PROPERTY_SEED}-{case_number}",
            "source_anchor": (
                "Dots-Boxes-AI.py:14-32, 76-80, 149-162"
            ),
            "input": args,
            "expected": expected,
            "reference": expected,
            "actual": actual,
        }
        results.append(result)
        print("R26_T014_CASE=" + json.dumps(result))
        _verify_result(dots_boxes, args, expected)

    assert len(results) == PROPERTY_CASE_COUNT, (
        f"expected {PROPERTY_CASE_COUNT} generated cases, got {len(results)}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
