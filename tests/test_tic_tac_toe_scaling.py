"""Headless correctness and bounded operation-count checks for Tic-Tac-Toe main."""

import importlib.util
import json
import os
from pathlib import Path
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "games"
    / "Tic-Tac-Toe"
    / "Tic-Tac-Toe.py"
)

# Source preconditions: main initializes a 9-cell board at line 57; BG and
# SURFACE palette constants are assigned at lines 9-10. Clicks are processed
# in the main loop at lines 213-221, which checks board-cell Rects in order.
# Size m below means the number of valid board-cell clicks queued in one frame.
SMALLEST_CLICKS = [(122, 344)]
SMALLEST_EXPECTED_BOARD = ["X", "", "", "", "", "", "", "", ""]
SMALLEST_EXPECTED_SCORES = {"X": 0, "O": 0, "D": 0}
SMALLEST_EXPECTED_COLLISIONS = 5

ORDINARY_CLICKS = [(122, 344), (280, 344), (280, 502)]
ORDINARY_EXPECTED_BOARD = ["X", "O", "", "", "X", "", "", "", ""]
ORDINARY_EXPECTED_SCORES = {"X": 0, "O": 0, "D": 0}
ORDINARY_EXPECTED_COLLISIONS = 16

LARGER_CLICKS = [
    (122, 344),
    (280, 344),
    (280, 502),
    (438, 344),
    (438, 660),
]
LARGER_EXPECTED_BOARD = ["X", "O", "O", "", "X", "", "", "", "X"]
LARGER_EXPECTED_SCORES = {"X": 1, "O": 0, "D": 0}
LARGER_EXPECTED_COLLISIONS = 32

CASES = [
    (
        "smallest-one-click",
        SMALLEST_CLICKS,
        SMALLEST_EXPECTED_BOARD,
        SMALLEST_EXPECTED_SCORES,
        SMALLEST_EXPECTED_COLLISIONS,
    ),
    (
        "ordinary-three-clicks",
        ORDINARY_CLICKS,
        ORDINARY_EXPECTED_BOARD,
        ORDINARY_EXPECTED_SCORES,
        ORDINARY_EXPECTED_COLLISIONS,
    ),
    (
        "larger-five-clicks",
        LARGER_CLICKS,
        LARGER_EXPECTED_BOARD,
        LARGER_EXPECTED_SCORES,
        LARGER_EXPECTED_COLLISIONS,
    ),
]


def _load_game():
    spec = importlib.util.spec_from_file_location("tic_tac_toe_game", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load Tic-Tac-Toe from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def game():
    return _load_game()


def _run_main(game, clicks, monkeypatch, count_operations):
    pygame.init()
    events = [
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": position},
        )
        for position in clicks
    ]
    batches = iter((events, [pygame.event.Event(pygame.QUIT)]))
    monkeypatch.setattr(pygame.event, "get", lambda: next(batches))
    monkeypatch.setattr(pygame.time, "Clock", lambda: _NoWaitClock())

    collision_checks = 0

    def profile(frame, event, argument):
        nonlocal collision_checks
        if event == "c_call" and getattr(argument, "__name__", "") == "collidepoint":
            collision_checks += 1

    started = time.perf_counter()
    if count_operations:
        sys.setprofile(profile)
    try:
        with pytest.raises(SystemExit):
            game.main()
    finally:
        if count_operations:
            sys.setprofile(None)
    elapsed = time.perf_counter() - started

    return (
        game.board.copy(),
        game.scores.copy(),
        collision_checks,
        elapsed,
    )


class _NoWaitClock:
    def tick(self, fps):
        return 0


def test_main_scaling_cases_preserve_results_and_count_cell_searches(
    game, monkeypatch
):
    evidence = []
    timing_by_size = {}

    for name, clicks, expected_board, expected_scores, expected_collisions in CASES:
        operation_samples = []
        timing_samples = []
        for repetition in range(5):
            board, scores, collisions, _ = _run_main(
                game, clicks, monkeypatch, count_operations=True
            )
            operation_samples.append(collisions)
            assert game.BG == (11, 11, 18)
            assert game.SURFACE == (24, 24, 36)
            assert board == expected_board, (
                f"{name}, operation repetition {repetition}: "
                f"expected board {expected_board!r}, got {board!r}"
            )
            assert scores == expected_scores, (
                f"{name}, operation repetition {repetition}: "
                f"expected scores {expected_scores!r}, got {scores!r}"
            )
            assert collisions == expected_collisions, (
                f"{name}, operation repetition {repetition}: "
                f"expected collision checks {expected_collisions}, "
                f"got {collisions}"
            )

        for repetition in range(5):
            board, scores, _, elapsed = _run_main(
                game, clicks, monkeypatch, count_operations=False
            )
            timing_samples.append(elapsed)
            assert board == expected_board, (
                f"{name}, timing repetition {repetition}: "
                f"expected board {expected_board!r}, got {board!r}"
            )
            assert scores == expected_scores, (
                f"{name}, timing repetition {repetition}: "
                f"expected scores {expected_scores!r}, got {scores!r}"
            )

        ordered = sorted(timing_samples)
        timing_summary = {
            "median_seconds": ordered[len(ordered) // 2],
            "range_seconds": [ordered[0], ordered[-1]],
        }
        timing_by_size[len(clicks)] = timing_summary
        evidence.append(
            {
                "case": name,
                "source_preconditions": (
                    "Tic-Tac-Toe.py:9-10 palette; line 57 nine-cell initial "
                    "board; lines 213-221 handle queued clicks and render"
                ),
                "expected_palette": {
                    "BG": (11, 11, 18),
                    "SURFACE": (24, 24, 36),
                },
                "actual_palette": {
                    "BG": game.BG,
                    "SURFACE": game.SURFACE,
                },
                "input_size_definition": "m = valid board-cell clicks in one frame",
                "input_size": len(clicks),
                "clicks": clicks,
                "expected_board": expected_board,
                "expected_scores": expected_scores,
                "expected_rect_collision_checks": expected_collisions,
                "actual_rect_collision_check_samples": operation_samples,
                "timing_repetitions": 5,
                "timing": timing_summary,
                "correctness_checked_outside_timed_interval": True,
            }
        )

    print("R26_T019_BENCHMARK=" + json.dumps(evidence))
    assert [len(case[1]) for case in CASES] == [1, 3, 5]
    assert list(timing_by_size) == [1, 3, 5]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
