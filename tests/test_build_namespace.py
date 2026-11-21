"""Tests for _build_namespace in Scientific-Graphing-Calculator.py (R26-T036).

Written BEFORE refactoring to capture existing behavior.
Every assertion uses literal expected values independently calculated.
Source: math/Scientific-Graphing-Calculator/Scientific-Graphing-Calculator.py
"""

import importlib.util
import math
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("matplotlib")

_SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Scientific-Graphing-Calculator"
    / "Scientific-Graphing-Calculator.py"
)


@pytest.fixture(scope="module")
def mod():
    """Import the calculator module."""
    spec = importlib.util.spec_from_file_location(
        "scientific_graphing_calculator", _SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ── Precondition anchors (source lines) ──────────────────────────────────
# Line 17: _UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
# Line 96: history = []


# ── Smallest valid input: x_val=None ─────────────────────────────────────

class TestBuildNamespaceNoX:
    """Smallest valid input: _build_namespace() with no arguments."""

    def test_returns_dict(self, mod):
        # Precondition: line 25 — builds dict from vars(math)
        result = mod._build_namespace()
        assert isinstance(result, dict)

    def test_contains_math_functions(self, mod):
        # Precondition: line 25 — {k: v for k, v in vars(math).items() if not k.startswith("_")}
        ns = mod._build_namespace()
        # Independently verified: math module exposes these names
        for name in ("sin", "cos", "tan", "log", "sqrt", "pi", "e", "factorial"):
            assert name in ns, f"missing math name '{name}'"
            assert ns[name] is getattr(math, name)

    def test_contains_abs_and_round(self, mod):
        # Precondition: line 26 — names["abs"] = abs; line 27 — names["round"] = round
        ns = mod._build_namespace()
        assert ns["abs"] is abs
        assert ns["round"] is round

    def test_no_x_key_when_none(self, mod):
        # Precondition: line 28 — if x_val is not None: names["x"] = x_val
        ns = mod._build_namespace()
        assert "x" not in ns

    def test_no_private_math_names(self, mod):
        # Precondition: line 25 — filter: not k.startswith("_")
        ns = mod._build_namespace()
        for key in ns:
            assert not key.startswith("_"), f"private name '{key}' leaked"

    def test_pi_equals_math_pi(self, mod):
        # Precondition: line 25 — pi comes from vars(math) when x_val is None
        ns = mod._build_namespace()
        assert ns["pi"] == pytest.approx(3.141592653589793)

    def test_e_equals_math_e(self, mod):
        # Precondition: line 25 — e comes from vars(math) when x_val is None
        ns = mod._build_namespace()
        assert ns["e"] == pytest.approx(2.718281828459045)

    def test_no_numpy_ufuncs_when_no_x(self, mod):
        # Precondition: numpy ufuncs only added inside `if x_val is not None` (line 28)
        ns = mod._build_namespace()
        # numpy.add is a ufunc; it should NOT appear when x_val is None
        assert ns.get("sin") is math.sin  # math version, not numpy


# ── Ordinary input: x_val = 2.0 ─────────────────────────────────────────

class TestBuildNamespaceWithX:
    """Ordinary input: _build_namespace(x_val=2.0)."""

    def test_x_is_set(self, mod):
        # Precondition: line 29 — names["x"] = x_val
        ns = mod._build_namespace(x_val=2.0)
        assert ns["x"] == 2.0

    def test_numpy_ufuncs_override_math(self, mod):
        # Precondition: lines 33-35 — numpy ufuncs replace math functions
        ns = mod._build_namespace(x_val=2.0)
        assert isinstance(ns["sin"], np.ufunc)

    def test_pi_is_numpy_pi(self, mod):
        # Precondition: line 36 — names["pi"] = np.pi
        ns = mod._build_namespace(x_val=2.0)
        assert ns["pi"] is np.pi

    def test_e_is_numpy_e(self, mod):
        # Precondition: line 37 — names["e"] = np.e
        ns = mod._build_namespace(x_val=2.0)
        assert ns["e"] is np.e

    def test_abs_overridden_by_numpy_absolute(self, mod):
        # Precondition: lines 33-35 — numpy ufunc loop replaces "abs" key
        # because numpy exposes np.absolute as a ufunc named "absolute",
        # and separately np.abs which is also np.absolute (a ufunc).
        # The ufunc iteration over vars(np) finds "absolute" (a ufunc) and
        # writes names["absolute"]; it also finds the alias "abs" is not a
        # ufunc directly, but np.absolute IS. Actually np.abs is np.absolute.
        # The key "absolute" is a ufunc and overwrites nothing, but the
        # original "abs" from builtins is NOT overwritten by ufunc iteration
        # because "abs" itself is not in vars(np) as a ufunc — np.abs is an
        # alias. Let's check what actually happens:
        ns = mod._build_namespace(x_val=2.0)
        # numpy.absolute is a ufunc; vars(np) includes "absolute" as a ufunc.
        # The key "abs" in vars(np) is np.absolute which IS a ufunc, so it
        # DOES get overwritten by the ufunc loop.
        assert isinstance(ns["abs"], np.ufunc)

    def test_round_still_present(self, mod):
        # Precondition: line 27 — names["round"] = round
        ns = mod._build_namespace(x_val=2.0)
        assert ns["round"] is round


# ── Return-type and mutation invariants ──────────────────────────────────

class TestBuildNamespaceInvariants:
    """Verify return type, no mutation of inputs, and idempotency."""

    def test_return_type_is_dict(self, mod):
        assert isinstance(mod._build_namespace(), dict)
        assert isinstance(mod._build_namespace(x_val=1.0), dict)

    def test_independent_calls_no_shared_state(self, mod):
        # Two calls must return independent dicts
        ns1 = mod._build_namespace()
        ns2 = mod._build_namespace()
        ns1["__injected"] = True
        assert "__injected" not in ns2

    def test_idempotent_keys(self, mod):
        # Same keys each call
        k1 = set(mod._build_namespace().keys())
        k2 = set(mod._build_namespace().keys())
        assert k1 == k2

    def test_idempotent_keys_with_x(self, mod):
        k1 = set(mod._build_namespace(x_val=1.0).keys())
        k2 = set(mod._build_namespace(x_val=1.0).keys())
        assert k1 == k2
