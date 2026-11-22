"""
Mutation-resistant regression tests for `is_browser` in games/Emoji-Memory-Game/Emoji-Memory-Game.py.

Task ID: R26-T060
Preconditions & Fixture Anchors:
- EMOJIS = ["🍎", "🚗", "⚽", "🐍", "🎧", "🔥", "🌈", "🚀"] (Emoji-Memory-Game.py, line 9)
- DIFFICULTY_TIME_LIMITS = {"1": 5, "2": 4, "3": 2}      (Emoji-Memory-Game.py, lines 12-16)
- is_browser definition                                   (Emoji-Memory-Game.py, line 26)
"""

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "games"
    / "Emoji-Memory-Game"
    / "Emoji-Memory-Game.py"
)


def load_module():
    """Load Emoji-Memory-Game module safely."""
    spec = importlib.util.spec_from_file_location("emoji_memory_game", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestEmojiMemoryIsBrowserContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_browser_platform_detection_emscripten(self):
        """Case 1: Smallest valid input domain boundary (Emscripten / Pyodide browser runtime).

        Preconditions:
        - Source line 9: EMOJIS = ["🍎", "🚗", "⚽", "🐍", "🎧", "🔥", "🌈", "🚀"]
        - Source line 12: DIFFICULTY_TIME_LIMITS = {"1": 5, "2": 4, "3": 2}
        - Literal input: sys.platform = "emscripten"
        """
        initial_emojis = list(self.module.EMOJIS)
        initial_limits = dict(self.module.DIFFICULTY_TIME_LIMITS)

        with patch("sys.platform", "emscripten"):
            result = self.module.is_browser()

            # Assert explicit expected value
            expected_result = True
            self.assertIs(
                result,
                expected_result,
                f"Expected is_browser() to return {expected_result} on emscripten, got {result}",
            )

            # Assert zero observable mutation on fixture anchors
            self.assertEqual(self.module.EMOJIS, initial_emojis)
            self.assertEqual(self.module.DIFFICULTY_TIME_LIMITS, initial_limits)

    def test_ordinary_desktop_platforms_return_false(self):
        """Case 2: Ordinary input domains (Linux, Darwin macOS, Windows).

        Preconditions:
        - Source line 9: EMOJIS anchor
        - Source line 12: DIFFICULTY_TIME_LIMITS anchor
        """
        for host_platform in ["darwin", "linux", "win32"]:
            with patch("sys.platform", host_platform):
                result = self.module.is_browser()
                expected_result = False
                self.assertIs(
                    result,
                    expected_result,
                    f"Expected is_browser() to return False on {host_platform}, got {result}",
                )

    def test_subtle_prefix_or_substring_rejection(self):
        """Case 3: Rejection of non-exact substring platforms (e.g., 'emscripten_custom', 'wasi').

        Protects against loose `in` containment mutations.
        """
        for near_platform in ["emscripten_v2", "not_emscripten", "wasi"]:
            with patch("sys.platform", near_platform):
                result = self.module.is_browser()
                self.assertIs(result, False)
