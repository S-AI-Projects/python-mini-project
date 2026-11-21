"""
Focused regression tests for `main` in games/Pygame-Chess/main.py.

Task ID: R26-T053
Preconditions & Source Line References:
- Line 9: def main()
- Line 18: initial renderer.draw(screen)
- Line 20: running = True
- Line 21: while running:
- Line 23: for event in pygame.event.get():
- Line 25: if event.type == pygame.QUIT: running = False
- Line 28: elif event.type == pygame.MOUSEBUTTONDOWN:
- Lines 30, 34: if not board.game_over():
- Line 32: input_handler.get_mouse_pos()
- Line 35: ai.computer_move()
- Line 37: renderer.draw(screen)
- Lines 39-41: if board.game_over(): pygame.time.wait(5000); running = False
"""

import importlib.util
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, call, patch

# Provide mock dependencies if pygame, chess, or stockfish are not installed in the environment
for mod in ["pygame", "chess", "stockfish"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

CHESS_DIR = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Pygame-Chess"
)
if str(CHESS_DIR) not in sys.path:
    sys.path.insert(0, str(CHESS_DIR))

MODULE_PATH = CHESS_DIR / "main.py"


def load_game_module():
    """Load Pygame-Chess main module safely via importlib."""
    spec = importlib.util.spec_from_file_location("pygame_chess_main", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChessMainOracle:
    """Independent reference oracle for games/Pygame-Chess/main.py loop domain.

    Calculates expected trace outputs without invoking main.py.
    """

    def evaluate(self, event_names, initial_game_over=False, game_over_after_clicks=None):
        draw_count = 1  # Line 18: initial renderer.draw(screen)
        mouse_handler_count = 0
        ai_move_count = 0
        wait_called = False
        game_over = initial_game_over

        running = True
        idx = 0

        while running:
            if game_over:
                wait_called = True
                running = False
                draw_count += 1
                break

            if idx < len(event_names):
                evt = event_names[idx]
                idx += 1

                if evt == "QUIT":
                    running = False
                elif evt == "MOUSEBUTTONDOWN":
                    if not game_over:
                        mouse_handler_count += 1
                        if (
                            game_over_after_clicks is not None
                            and mouse_handler_count >= game_over_after_clicks
                        ):
                            game_over = True
                        if not game_over:
                            ai_move_count += 1
            else:
                running = False

            draw_count += 1

            if game_over:
                wait_called = True
                running = False

        return {
            "return_value": None,
            "draw_count": draw_count,
            "mouse_handler_count": mouse_handler_count,
            "ai_move_count": ai_move_count,
            "wait_called": wait_called,
            "terminated": not running,
        }


class TestPygameChessMainDomain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()
        cls.oracle = ChessMainOracle()

    def run_main_with_events(
        self,
        event_names,
        initial_game_over=False,
        game_over_after_clicks=None,
    ):
        """Execute main under controlled mock environment and capture execution trace."""
        mock_pygame = MagicMock()
        mock_pygame.QUIT = 256
        mock_pygame.MOUSEBUTTONDOWN = 1025
        mock_pygame.KEYDOWN = 768
        mock_pygame.KEYUP = 769
        mock_pygame.MOUSEMOTION = 1024
        mock_pygame.ACTIVEEVENT = 1
        mock_pygame.VIDEORESIZE = 16
        mock_pygame.USEREVENT = 24

        event_code_map = {
            "QUIT": mock_pygame.QUIT,
            "MOUSEBUTTONDOWN": mock_pygame.MOUSEBUTTONDOWN,
            "KEYDOWN": mock_pygame.KEYDOWN,
            "KEYUP": mock_pygame.KEYUP,
            "MOUSEMOTION": mock_pygame.MOUSEMOTION,
            "ACTIVEEVENT": mock_pygame.ACTIVEEVENT,
            "VIDEORESIZE": mock_pygame.VIDEORESIZE,
            "USEREVENT": mock_pygame.USEREVENT,
        }

        # Build stream of mock events returned by pygame.event.get()
        event_objs = []
        for name in event_names:
            e = MagicMock()
            e.type = event_code_map.get(name, 9999)
            event_objs.append(e)

        # pygame.event.get yields events one batch at a time
        batches = [[e] for e in event_objs] + [[]]
        batch_iter = iter(batches)

        mock_pygame.event.get = lambda: next(batch_iter, [])

        # Mock subcomponents
        mock_screen = MagicMock()
        mock_pygame.display.set_mode.return_value = mock_screen

        click_counter = [0]

        def is_game_over():
            if initial_game_over:
                return True
            if (
                game_over_after_clicks is not None
                and click_counter[0] >= game_over_after_clicks
            ):
                return True
            return False

        mock_board = MagicMock()
        mock_board.game_over = is_game_over

        mock_input_handler = MagicMock()

        def handle_mouse():
            click_counter[0] += 1

        mock_input_handler.get_mouse_pos = MagicMock(side_effect=handle_mouse)

        mock_ai = MagicMock()
        mock_renderer = MagicMock()
        mock_loader = MagicMock()

        with patch.object(self.module, "pygame", mock_pygame), \
             patch.object(self.module, "Board", return_value=mock_board), \
             patch.object(self.module, "InputHandler", return_value=mock_input_handler), \
             patch.object(self.module, "AiEngine", return_value=mock_ai), \
             patch.object(self.module, "Renderer", return_value=mock_renderer), \
             patch.object(self.module, "Loader", return_value=mock_loader):

            actual_return = self.module.main()

        return {
            "return_value": actual_return,
            "draw_count": mock_renderer.draw.call_count,
            "mouse_handler_count": mock_input_handler.get_mouse_pos.call_count,
            "ai_move_count": mock_ai.computer_move.call_count,
            "wait_called": mock_pygame.time.wait.called,
            "terminated": True,
        }

    def test_smallest_valid_input(self):
        """Test Case 1: Smallest valid input domain ([QUIT]).

        Precondition: Line 25: if event.type == pygame.QUIT: running = False
        """
        events = ["QUIT"]
        expected = self.oracle.evaluate(events)
        actual = self.run_main_with_events(events)

        self.assertIsNone(
            actual["return_value"],
            f"Expected return value None, got {actual['return_value']!r}",
        )
        self.assertEqual(
            actual["draw_count"],
            expected["draw_count"],
            f"Expected {expected['draw_count']} draws, got {actual['draw_count']}",
        )
        self.assertEqual(
            actual["mouse_handler_count"],
            0,
            "Expected 0 mouse handler calls for immediate quit",
        )
        self.assertEqual(
            actual["ai_move_count"],
            0,
            "Expected 0 AI move calls for immediate quit",
        )
        self.assertFalse(actual["wait_called"], "Expected wait not called")
        self.assertTrue(actual["terminated"], "Expected loop termination")

    def test_ordinary_input(self):
        """Test Case 2: Ordinary input ([MOUSEBUTTONDOWN, QUIT]).

        Preconditions: Lines 28, 32, 35, 25
        """
        events = ["MOUSEBUTTONDOWN", "QUIT"]
        expected = self.oracle.evaluate(events)
        actual = self.run_main_with_events(events)

        self.assertIsNone(actual["return_value"])
        self.assertEqual(actual["draw_count"], expected["draw_count"])
        self.assertEqual(actual["mouse_handler_count"], 1)
        self.assertEqual(actual["ai_move_count"], 1)
        self.assertFalse(actual["wait_called"])
        self.assertTrue(actual["terminated"])

    def test_21_small_valid_inputs_oracle_comparison(self):
        """Test Case 3: Enumerate and compare 21 small valid inputs against the oracle."""
        test_inputs = [
            # 1. Immediate quit (smallest valid input)
            (["QUIT"], False, None),
            # 2-7. Ignored non-interactive events
            (["KEYDOWN", "QUIT"], False, None),
            (["KEYUP", "QUIT"], False, None),
            (["MOUSEMOTION", "QUIT"], False, None),
            (["ACTIVEEVENT", "QUIT"], False, None),
            (["VIDEORESIZE", "QUIT"], False, None),
            (["USEREVENT", "QUIT"], False, None),
            # 8-11. Multi-click sequences
            (["MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "MOUSEBUTTONDOWN", "MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN"] * 4 + ["QUIT"], False, None),
            # 12-18. Interleaved interactive and ignored events
            (["KEYDOWN", "MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEMOTION", "MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "KEYDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "MOUSEMOTION", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "MOUSEBUTTONDOWN", "KEYDOWN", "QUIT"], False, None),
            (["KEYDOWN", "KEYUP", "MOUSEBUTTONDOWN", "QUIT"], False, None),
            (["MOUSEBUTTONDOWN", "USEREVENT", "QUIT"], False, None),
            # 19. Mouse click triggers game over
            (["MOUSEBUTTONDOWN"], False, 1),
            # 20. Initial game over state
            ([], True, None),
            # 21. Quit followed by pending event
            (["QUIT", "MOUSEBUTTONDOWN"], False, None),
        ]

        self.assertEqual(
            len(test_inputs),
            21,
            f"Expected at least 20 enumerated inputs, got {len(test_inputs)}",
        )

        for i, (events, init_game_over, click_game_over) in enumerate(test_inputs, start=1):
            with self.subTest(case_number=i, events=events):
                expected = self.oracle.evaluate(
                    events,
                    initial_game_over=init_game_over,
                    game_over_after_clicks=click_game_over,
                )
                actual = self.run_main_with_events(
                    events,
                    initial_game_over=init_game_over,
                    game_over_after_clicks=click_game_over,
                )

                self.assertEqual(
                    actual["return_value"],
                    expected["return_value"],
                    f"Case {i}: return value mismatch",
                )
                self.assertEqual(
                    actual["draw_count"],
                    expected["draw_count"],
                    f"Case {i} ({events}): draw count expected {expected['draw_count']}, got {actual['draw_count']}",
                )
                self.assertEqual(
                    actual["mouse_handler_count"],
                    expected["mouse_handler_count"],
                    f"Case {i}: mouse handler count expected {expected['mouse_handler_count']}, got {actual['mouse_handler_count']}",
                )
                self.assertEqual(
                    actual["ai_move_count"],
                    expected["ai_move_count"],
                    f"Case {i}: AI move count expected {expected['ai_move_count']}, got {actual['ai_move_count']}",
                )
                self.assertEqual(
                    actual["wait_called"],
                    expected["wait_called"],
                    f"Case {i}: wait_called expected {expected['wait_called']}, got {actual['wait_called']}",
                )
                self.assertEqual(
                    actual["terminated"],
                    expected["terminated"],
                    f"Case {i}: terminated expected {expected['terminated']}, got {actual['terminated']}",
                )


if __name__ == "__main__":
    unittest.main()
