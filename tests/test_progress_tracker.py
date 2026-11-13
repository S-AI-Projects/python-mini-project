"""Contract tests for the Progress Tracker's saved-progress loader."""

import copy
import importlib.util
import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "utilities" / "Progress-Tracker" / "Progress-Tracker.py"
EVIDENCE_DIR = ROOT / "work" / "R26-T011"
DATA_FILE = "/fixture/completed_projects.json"

# Progress-Tracker.py:16-26 establishes the three buckets and category map.
# Its lines 31-37 use each fixture row's category and path to populate them.
REGISTRY_INPUT = [
    {"category": "games", "path": "games/Rolling-Dice/main.py"},
    {"category": "math", "path": "math/Pascal-Triangle/main.py"},
    {
        "category": "utilities",
        "path": "utilities/Progress-Tracker/Progress-Tracker.py",
    },
]

CASE_RESULTS = []


def _load_tracker():
    spec = importlib.util.spec_from_file_location("progress_tracker", SOURCE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Progress Tracker module from {SOURCE}")

    tracker = importlib.util.module_from_spec(spec)
    registry_file = mock_open(read_data=json.dumps(REGISTRY_INPUT))
    with patch("builtins.open", registry_file):
        spec.loader.exec_module(tracker)
    return tracker


def _record(case, source_anchor, input_data, expected_return, actual_return,
            expected_saved, actual_saved):
    result = {
        "case": case,
        "source_anchor": source_anchor,
        "input": input_data,
        "expected_return": expected_return,
        "actual_return": actual_return,
        "expected_saved": expected_saved,
        "actual_saved": actual_saved,
    }
    CASE_RESULTS.append(result)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (EVIDENCE_DIR / "inputs.json").write_text(
        json.dumps(
            [{"case": item["case"], "source_anchor": item["source_anchor"],
              "input": item["input"]} for item in CASE_RESULTS],
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "expected.json").write_text(
        json.dumps(
            [{"case": item["case"], "return": item["expected_return"],
              "saved": item["expected_saved"]} for item in CASE_RESULTS],
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    (EVIDENCE_DIR / "actual.json").write_text(
        json.dumps(CASE_RESULTS, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


@pytest.fixture
def tracker(monkeypatch):
    module = _load_tracker()
    monkeypatch.setattr(module, "DATA_FILE", DATA_FILE)
    return module


def _load_with_fixture(tracker, input_data, file_exists=True):
    input_text = json.dumps(input_data) if input_data is not None else ""
    data_file = mock_open(read_data=input_text)
    saved = []

    def save_data(data):
        saved.append(copy.deepcopy(data))

    with patch.object(tracker.os.path, "exists", return_value=file_exists), \
            patch.object(tracker, "open", data_file, create=True), \
            patch.object(tracker, "save_data", side_effect=save_data):
        actual = tracker.load_data()
    return actual, saved, data_file


def test_missing_file_returns_fresh_progress(tracker):
    # Preconditions: lines 55 and 83-84 select the fresh-state branch.
    input_data = None
    expected = {"completed": {}}
    actual, saved, data_file = _load_with_fixture(
        tracker, input_data, file_exists=False
    )
    expected_saved = []

    _record("missing file", "Progress-Tracker.py:55, 83-84", input_data,
            expected, actual, expected_saved, saved)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert saved == expected_saved, (
        f"expected no save calls {expected_saved!r}, got {saved!r}"
    )
    assert data_file.call_count == 0, (
        f"expected no file open, got {data_file.call_count} calls"
    )


def test_smallest_valid_file_returns_empty_progress(tracker):
    # Preconditions: lines 55-57 load the file; line 64 defaults completed.
    input_data = {"completed": {}}
    expected = {"completed": {}}
    actual, saved, _ = _load_with_fixture(tracker, input_data)
    expected_saved = []

    _record("smallest valid file", "Progress-Tracker.py:55-57, 64, 83",
            input_data, expected, actual, expected_saved, saved)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert saved == expected_saved, (
        f"expected no save calls {expected_saved!r}, got {saved!r}"
    )


def test_ordinary_progress_is_preserved(tracker):
    # Preconditions: lines 64 and 67-83 preserve non-migration entries.
    input_data = {
        "completed": {"Snake-Game": "2026-11-01 10:00"}
    }
    expected = {
        "completed": {"Snake-Game": "2026-11-01 10:00"}
    }
    actual, saved, _ = _load_with_fixture(tracker, input_data)
    expected_saved = []

    _record("ordinary progress", "Progress-Tracker.py:64, 67-83", input_data,
            expected, actual, expected_saved, saved)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert saved == expected_saved, (
        f"expected no save calls {expected_saved!r}, got {saved!r}"
    )


def test_repeated_timestamps_preserve_distinct_projects(tracker):
    # Preconditions: lines 67-79 iterate and retain each completed project.
    input_data = {
        "completed": {
            "Snake-Game": "2026-11-01 10:00",
            "Chess": "2026-11-01 10:00",
        }
    }
    expected = {
        "completed": {
            "Snake-Game": "2026-11-01 10:00",
            "Chess": "2026-11-01 10:00",
        }
    }
    actual, saved, _ = _load_with_fixture(tracker, input_data)
    expected_saved = []

    _record("repeated timestamps", "Progress-Tracker.py:67-79", input_data,
            expected, actual, expected_saved, saved)
    assert actual == expected, f"expected {expected!r}, got {actual!r}"
    assert saved == expected_saved, (
        f"expected no save calls {expected_saved!r}, got {saved!r}"
    )


def test_valid_legacy_name_is_returned_and_persisted(tracker):
    # The fixture maps "games" via lines 22-25 and adds Rolling-Dice via
    # lines 31-37. Lines 59-71 migrate only when that target is registered.
    expected_projects = {
        "🎲 Games": ["Rolling-Dice"],
        "🔢 Math": ["Pascal-Triangle"],
        "🔐 Utilities": ["Progress-Tracker"],
    }
    actual_projects = tracker.ALL_PROJECTS
    assert actual_projects == expected_projects, (
        f"expected registry categories {expected_projects!r}, "
        f"got {actual_projects!r}"
    )
    expected_target_is_registered = True
    actual_target_is_registered = "Rolling-Dice" in tracker.ALL_PROJECT_NAMES
    assert actual_target_is_registered is expected_target_is_registered, (
        f"expected target registered={expected_target_is_registered}, "
        f"got {actual_target_is_registered}"
    )
    input_data = {
        "completed": {
            "Dice-Rolling": "2026-11-01 10:00",
            "Snake-Game": "2026-11-01 11:00",
        }
    }
    expected = {
        "completed": {
            "Rolling-Dice": "2026-11-01 10:00",
            "Snake-Game": "2026-11-01 11:00",
        }
    }
    actual, saved, _ = _load_with_fixture(tracker, input_data)
    expected_saved = [expected]

    _record("legacy migration mutation",
            "Progress-Tracker.py:16-26, 31-37, 59-71, 80-83",
            input_data, expected, actual, expected_saved, saved)
    assert actual == expected, f"expected return {expected!r}, got {actual!r}"
    assert saved == expected_saved, (
        f"expected persisted values {expected_saved!r}, got {saved!r}"
    )
