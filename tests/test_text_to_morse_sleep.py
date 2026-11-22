"""
Property and contract regression tests for `_sleep_ms` in utilities/Text-to-Morse/Text-to-Morse.py.

Task ID: R26-T054
Preconditions & Fixture Anchors:
- morse_result = []       (Text-to-Morse.py, line 109)
- unsupported_chars = []  (Text-to-Morse.py, line 110)
- DOT_DURATION = 100      (Text-to-Morse.py, line 29)
- DASH_DURATION = 300     (Text-to-Morse.py, line 30)
- _sleep_ms definition    (Text-to-Morse.py, line 37)
"""

import importlib.util
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "utilities"
    / "Text-to-Morse"
    / "Text-to-Morse.py"
)


def load_module():
    """Load Text-to-Morse module safely."""
    spec = importlib.util.spec_from_file_location("text_to_morse", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch("sys.stdout"):
        spec.loader.exec_module(module)
    return module


class TestSleepMsInvariant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_smallest_valid_input_zero_ms(self):
        """Case 1: Smallest valid input domain boundary (ms = 0).

        Preconditions:
        - Line 109: morse_result = [] (empty fixture anchor)
        - Line 110: unsupported_chars = [] (empty fixture anchor)
        - Line 37: def _sleep_ms(ms: int)
        Literal inputs: ms = 0
        """
        fixture_morse_result = []
        fixture_unsupported_chars = []

        with patch("time.sleep") as mock_sleep:
            result = self.module._sleep_ms(0)

            # Assert return value contract
            self.assertIs(result, None, f"Expected return None, got {result}")

            # Assert time.sleep called with 0.0 seconds
            mock_sleep.assert_called_once_with(0.0)

            # Assert zero observable mutation
            self.assertEqual(
                fixture_morse_result,
                [],
                "morse_result unexpectedly mutated on ms=0",
            )
            self.assertEqual(
                fixture_unsupported_chars,
                [],
                "unsupported_chars unexpectedly mutated on ms=0",
            )

    def test_ordinary_valid_input_dot_duration(self):
        """Case 2: Ordinary input from DOT_DURATION (ms = 100).

        Preconditions:
        - Line 29: DOT_DURATION = 100 ms
        - Line 109: morse_result = [] -> populated
        - Line 110: unsupported_chars = [] -> populated
        Literal inputs: ms = 100
        """
        fixture_morse_result = [".-", "-..."]
        fixture_unsupported_chars = ["$", "@"]

        with patch("time.sleep") as mock_sleep:
            result = self.module._sleep_ms(100)

            # Assert return value contract
            self.assertIs(result, None, f"Expected return None, got {result}")

            # Assert time.sleep called with 0.1 seconds (100 / 1000.0)
            mock_sleep.assert_called_once_with(0.1)

            # Assert zero observable mutation
            self.assertEqual(fixture_morse_result, [".-", "-..."])
            self.assertEqual(fixture_unsupported_chars, ["$", "@"])

    def test_invariant_random_property_generator(self):
        """Case 3: Property invariant check over 100 deterministic pseudo-random inputs.

        Invariant guarantees:
        1. return value is strictly None.
        2. time.sleep duration == ms / 1000.0.
        3. Monotonic ordering: ms1 <= ms2 implies duration(ms1) <= duration(ms2).
        4. External state remains strictly unmutated.
        """
        rng = random.Random(42)  # Deterministic seed
        samples = [rng.randint(0, 5000) for _ in range(100)]

        fixture_morse_result = ["--."]
        fixture_unsupported_chars = []

        durations_recorded = []

        for ms in samples:
            with patch("time.sleep") as mock_sleep:
                ret = self.module._sleep_ms(ms)
                self.assertIs(ret, None)
                expected_seconds = ms / 1000.0
                mock_sleep.assert_called_once_with(expected_seconds)
                durations_recorded.append((ms, expected_seconds))

        # Check monotonicity invariant
        sorted_by_ms = sorted(durations_recorded, key=lambda x: x[0])
        for i in range(len(sorted_by_ms) - 1):
            ms_curr, dur_curr = sorted_by_ms[i]
            ms_next, dur_next = sorted_by_ms[i + 1]
            self.assertLessEqual(
                dur_curr,
                dur_next,
                f"Monotonicity invariant violated between {ms_curr}ms and {ms_next}ms",
            )

        # Check fixture mutation
        self.assertEqual(fixture_morse_result, ["--."])
        self.assertEqual(fixture_unsupported_chars, [])
