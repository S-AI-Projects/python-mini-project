"""
Tests for math/Prime-Number-Analyzer/Prime-Number-Analyzer.py

Focus areas (Task R26-T035):
- Make verification repeatable for is_prime(num: int) -> bool.
- Pure function verification: repeated calls and state isolation.
- Fixture: Supported domain around 1, 2, 9 and 11.
- Sieve through 12: primes are 2, 3, 5, 7, 11 (respecting exclusive upper-bound interface).
- Repeatability contract: Run fixture twice in fresh state and once after other valid inputs;
  assert earlier runs cannot alter later results.
- Zero external dependencies: no network, no live user account, no GUI interactions.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Prime-Number-Analyzer"
    / "Prime-Number-Analyzer.py"
)


def load_prime_analyzer():
    spec = importlib.util.spec_from_file_location("prime_analyzer", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prime_analyzer"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def pna():
    return load_prime_analyzer()


# ── Domain around 1, 2, 9, 11 ───────────────────────────────────────────────

def test_is_prime_domain_around_one(pna):
    """
    Precondition source lines: Lines 14-15 (if num < 2: return False).
    Domain around 1: 0 -> False, 1 -> False (primes must be strictly > 1).
    """
    assert pna.is_prime(0) is False, "Expected 0 to be non-prime"
    assert pna.is_prime(1) is False, "Expected 1 to be non-prime"


def test_is_prime_domain_around_two(pna):
    """
    Precondition source lines:
      Lines 16-17: if num == 2: return True
      Lines 18-19: if num % 2 == 0: return False
    Domain around 2:
      2 -> True (smallest prime and only even prime)
      3 -> True
      4 -> False (even composite)
    """
    assert pna.is_prime(2) is True, "Expected 2 to be prime"
    assert pna.is_prime(3) is True, "Expected 3 to be prime"
    assert pna.is_prime(4) is False, "Expected 4 to be non-prime"


def test_is_prime_domain_around_nine(pna):
    """
    Precondition source lines:
      Lines 20-22: for i in range(3, int(math.sqrt(num)) + 1, 2): if num % i == 0: return False
    Domain around 9:
      8 -> False (even composite)
      9 -> False (3 x 3, smallest odd composite)
      10 -> False (even composite)
    """
    assert pna.is_prime(8) is False, "Expected 8 to be non-prime"
    assert pna.is_prime(9) is False, "Expected 9 to be non-prime (divisible by 3)"
    assert pna.is_prime(10) is False, "Expected 10 to be non-prime"


def test_is_prime_domain_around_eleven(pna):
    """
    Precondition source lines:
      Line 20-23: loops without finding divisor, returns True.
    Domain around 11:
      11 -> True (prime)
      12 -> False (composite)
      13 -> True (prime)
    """
    assert pna.is_prime(11) is True, "Expected 11 to be prime"
    assert pna.is_prime(12) is False, "Expected 12 to be non-prime"
    assert pna.is_prime(13) is True, "Expected 13 to be prime"


# ── Sieve through 12 with Exclusive Upper Bound ─────────────────────────────

def test_sieve_through_twelve_exclusive_upper_bound(pna):
    """
    Goal requirement:
    For a sieve through 12 the primes are 2, 3, 5, 7 and 11;
    respect an exclusive upper-bound interface.
    Range: range(2, 12) -> exclusive upper bound 12.
    """
    upper_bound_exclusive = 12
    evaluated_primes = [n for n in range(2, upper_bound_exclusive) if pna.is_prime(n)]
    expected_primes = [2, 3, 5, 7, 11]

    assert evaluated_primes == expected_primes, (
        f"Expected primes {expected_primes}, got {evaluated_primes}"
    )

    evaluated_non_primes = [n for n in range(2, upper_bound_exclusive) if not pna.is_prime(n)]
    expected_non_primes = [4, 6, 8, 9, 10]
    assert evaluated_non_primes == expected_non_primes


# ── Repeatability & Isolation Requirements ──────────────────────────────────

def test_is_prime_repeatability_across_fresh_and_interleaved_runs(pna):
    """
    Step 3 requirement:
    Run the same fixture twice in fresh isolated state and once after another valid input;
    assert that earlier runs cannot alter the later result.
    Fixture: [1, 2, 9, 11]
    Expected: [False, True, False, True]
    """
    fixture_inputs = [1, 2, 9, 11]
    expected_outputs = [False, True, False, True]

    # Run 1: Fresh state
    run_1 = [pna.is_prime(n) for n in fixture_inputs]
    assert run_1 == expected_outputs, f"Run 1 mismatch: {run_1}"

    # Run 2: Fresh re-evaluation
    fresh_pna = load_prime_analyzer()
    run_2 = [fresh_pna.is_prime(n) for n in fixture_inputs]
    assert run_2 == expected_outputs, f"Run 2 mismatch: {run_2}"

    # Interleaving with other valid inputs
    other_inputs = [997, 100, 17, 49, 101, 0, -7]
    _ = [pna.is_prime(n) for n in other_inputs]

    # Run 3: Evaluated after intervening operations
    run_3 = [pna.is_prime(n) for n in fixture_inputs]
    assert run_3 == expected_outputs, f"Run 3 mismatch after interleaving: {run_3}"

    # Assert complete invariance
    assert run_1 == run_2 == run_3


def test_is_prime_pure_function_input_isolation(pna):
    """
    Verify input value isolation and lack of state mutation.
    """
    num = 11
    res = pna.is_prime(num)
    assert res is True
    assert num == 11, "Input variable was mutated"


def test_is_prime_negative_numbers(pna):
    """
    Precondition source lines: Lines 14-15 (if num < 2: return False).
    Negative numbers must return False.
    """
    for neg in [-1, -2, -10, -997]:
        assert pna.is_prime(neg) is False, f"Expected negative {neg} to be non-prime"
