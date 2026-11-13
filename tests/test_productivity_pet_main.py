"""Fixture-based behavior checks for Productivity Pet main task accounting."""

import importlib.util
import json
from datetime import datetime as real_datetime
from pathlib import Path
from unittest.mock import patch

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "utilities"
    / "Productivity-Pet"
    / "Productivity-Pet.py"
)

# Before refactoring, main at line 9 initialized `tasks = []` and
# `completed_task_list = []` at lines 95-98. After extraction, main at line 32
# initializes `tasks` at line 118 and `_calculate_task_rewards` initializes
# `completed_task_list` at line 11.
FIXED_TODAY = "2026-11-13"
INITIAL_DATA = {
    "xp": 0,
    "level": 1,
    "coins": 0,
    "streak": 0,
    "best_streak": 0,
    "completed_tasks": 0,
    "achievements": [],
    "pet_class": "Fox 🦊",
    "last_day": "2026-11-12",
    "history": [],
}

SMALLEST_INPUTS = ["yes", "1", "Read", "easy", "yes", "n"]
SMALLEST_EXPECTED_DATA = {
    "xp": 5,
    "level": 1,
    "coins": 15,
    "streak": 1,
    "best_streak": 1,
    "completed_tasks": 1,
    "achievements": ["🥚 First Steps", "👑 Legendary Focus"],
    "pet_class": "Fox 🦊",
    "last_day": FIXED_TODAY,
    "history": [
        {
            "date": FIXED_TODAY,
            "total_tasks": 1,
            "completed": 1,
            "percentage": 100.0,
            "tasks": ["Read"],
        }
    ],
}
SMALLEST_EXPECTED_OUTPUT = [
    "📊 Progress: 100.0%",
    "💭 Pet Mood: 😄 Motivated",
    "✨ XP Earned: +5",
    "🪙 Coins Earned: +15",
]

ORDINARY_INPUTS = [
    "yes",
    "3",
    "Read",
    "easy",
    "yes",
    "Walk",
    "medium",
    "no",
    "Plan",
    "hard",
    "yes",
    "n",
]
ORDINARY_EXPECTED_DATA = {
    "xp": 35,
    "level": 1,
    "coins": 20,
    "streak": 1,
    "best_streak": 1,
    "completed_tasks": 2,
    "achievements": ["🥚 First Steps"],
    "pet_class": "Fox 🦊",
    "last_day": FIXED_TODAY,
    "history": [
        {
            "date": FIXED_TODAY,
            "total_tasks": 3,
            "completed": 2,
            "percentage": 66.7,
            "tasks": ["Read", "Plan"],
        }
    ],
}
ORDINARY_EXPECTED_OUTPUT = [
    "📊 Progress: 66.7%",
    "💭 Pet Mood: 😐 Neutral",
    "✨ XP Earned: +35",
    "🪙 Coins Earned: +20",
]


def _load_productivity_pet():
    spec = importlib.util.spec_from_file_location("productivity_pet", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Productivity Pet from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def productivity_pet(tmp_path):
    module = _load_productivity_pet()
    module.SAVE_FILE = tmp_path / "save.json"
    module.SAVE_FILE.write_text(json.dumps(INITIAL_DATA), encoding="utf-8")

    class FixedDateTime:
        @classmethod
        def now(cls):
            return real_datetime(2026, 11, 13)

    module.datetime = FixedDateTime
    return module


def _run_case(module, inputs, capsys, name, expected_data, expected_output):
    with patch("builtins.input", side_effect=inputs):
        with patch.object(module.random, "randint", return_value=100):
            with patch.object(module.random, "choice") as random_choice:
                result = module.main()

    output = capsys.readouterr().out
    actual_data = json.loads(module.SAVE_FILE.read_text(encoding="utf-8"))
    evidence = {
        "case": name,
        "source_preconditions": (
            "before: main at Productivity-Pet.py:9 initializes tasks=[] and "
            "completed_task_list=[] at lines 95-98; after: main at line 32 "
            "initializes tasks at line 118 and _calculate_task_rewards at "
            "line 9 initializes completed_task_list at line 11"
        ),
        "inputs": inputs,
        "expected_output": expected_output,
        "actual_output": [line for line in expected_output if line in output],
        "expected_saved_data": expected_data,
        "actual_saved_data": actual_data,
        "expected_return": None,
        "actual_return": result,
        "random_event_roll": 100,
        "random_choice_called": random_choice.called,
    }
    with capsys.disabled():
        print("R26_T016_CASE=" + json.dumps(evidence, ensure_ascii=False))

    assert result is None, f"{name}: expected return None, got {result!r}"
    assert actual_data == expected_data, (
        f"{name}: expected saved data {expected_data!r}, got {actual_data!r}"
    )
    assert all(line in output for line in expected_output), (
        f"{name}: expected output lines {expected_output!r}, got {output!r}"
    )
    assert not random_choice.called, (
        f"{name}: no random event should be selected for a roll of 100"
    )


def test_main_accounts_for_one_completed_task(productivity_pet, capsys):
    _run_case(
        productivity_pet,
        SMALLEST_INPUTS,
        capsys,
        "smallest valid task list",
        SMALLEST_EXPECTED_DATA,
        SMALLEST_EXPECTED_OUTPUT,
    )


def test_main_accounts_for_mixed_task_list(productivity_pet, capsys):
    _run_case(
        productivity_pet,
        ORDINARY_INPUTS,
        capsys,
        "ordinary mixed task list",
        ORDINARY_EXPECTED_DATA,
        ORDINARY_EXPECTED_OUTPUT,
    )
