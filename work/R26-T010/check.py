#!/usr/bin/env python3
"""
Independent focused checker for R26-T010 (Fourier-Series-Visualizer.py).

Validates:
- Source precondition anchors in Fourier-Series-Visualizer.py (main, bounds, circles, radii_lines, return order).
- Independent execution of main() against literal fixtures and hand-derived expected outputs in cases.json.
- Output type (None), artist count/shape/ordering, and caller-input non-mutation.
- Repeatability across fresh equivalent inputs under controlled external state.
- Native pytest execution for tests/test_fourier_series_visualizer.py with nonzero pass count.
"""

import argparse
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import types
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TARGET = (
    REPO_ROOT
    / "math"
    / "Fourier-Series-Visualizer"
    / "Fourier-Series-Visualizer.py"
)
DEFAULT_CASES = Path(__file__).resolve().parent / "cases.json"
TEST_FILE = REPO_ROOT / "tests" / "test_fourier_series_visualizer.py"


class _SimpleArray:
    """Minimal array shim supporting scalar + and * when numpy is not installed."""

    def __init__(self, values):
        self._values = [float(v) for v in values]

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __getitem__(self, idx):
        return self._values[idx]

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return _SimpleArray(v + other for v in self._values)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return _SimpleArray(v * other for v in self._values)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)


def _build_fake_numpy():
    np_mod = types.ModuleType("numpy")
    np_mod.pi = math.pi

    def linspace(start, stop, num):
        count = int(num)
        if count <= 0:
            return _SimpleArray([])
        if count == 1:
            return _SimpleArray([float(start)])
        values = [float(start + (stop - start) * i / (count - 1)) for i in range(count - 1)]
        values.append(float(stop))
        return _SimpleArray(values)

    def cos(x):
        if isinstance(x, (int, float)):
            return math.cos(x)
        return _SimpleArray(math.cos(v) for v in x)

    def sin(x):
        if isinstance(x, (int, float)):
            return math.sin(x)
        return _SimpleArray(math.sin(v) for v in x)

    np_mod.linspace = linspace
    np_mod.cos = cos
    np_mod.sin = sin
    return np_mod


def load_target_module(target_path: Path, module_name: str):
    """Import only the target module with safe stubs when optional GUI packages are absent."""
    os.environ.setdefault("MPLBACKEND", "Agg")
    injected = []
    saved = {}

    def _inject(name, obj):
        if name in sys.modules:
            saved[name] = sys.modules[name]
        else:
            injected.append(name)
        sys.modules[name] = obj

    try:
        import numpy  # noqa: F401
    except ImportError:
        _inject("numpy", _build_fake_numpy())

    try:
        import matplotlib.pyplot  # noqa: F401
        from matplotlib.animation import FuncAnimation  # noqa: F401
    except ImportError:
        mpl_mod = types.ModuleType("matplotlib")
        pyplot_mod = types.ModuleType("matplotlib.pyplot")
        pyplot_mod.subplots = lambda *args, **kwargs: (None, None)
        pyplot_mod.show = lambda *args, **kwargs: None
        anim_mod = types.ModuleType("matplotlib.animation")
        anim_mod.FuncAnimation = lambda *args, **kwargs: None
        mpl_mod.pyplot = pyplot_mod
        mpl_mod.animation = anim_mod
        _inject("matplotlib", mpl_mod)
        _inject("matplotlib.pyplot", pyplot_mod)
        _inject("matplotlib.animation", anim_mod)

    try:
        spec = importlib.util.spec_from_file_location(module_name, target_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create module spec for {target_path}")
        mod = types.ModuleType(module_name)
        mod.__file__ = str(target_path)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        for name in injected:
            sys.modules.pop(name, None)
        for name, orig in saved.items():
            sys.modules[name] = orig


class _SpyArtist:
    def __init__(self):
        self.last_data = None

    def set_data(self, xdata, ydata):
        self.last_data = ([float(v) for v in xdata], [float(v) for v in ydata])


class _SpyAxes:
    def __init__(self):
        self.title = None
        self.xlim = None
        self.ylim = None
        self.artists = []

    def set_title(self, title):
        self.title = title

    def set_xlim(self, left, right):
        self.xlim = (left, right)

    def set_ylim(self, bottom, top):
        self.ylim = (bottom, top)

    def set_aspect(self, *_args, **_kwargs):
        pass

    def grid(self, *_args, **_kwargs):
        pass

    def plot(self, *_args, **_kwargs):
        artist = _SpyArtist()
        self.artists.append(artist)
        return (artist,)


def run_case(module, inputs, frames):
    sessions = []

    class _MockPlt:
        def subplots(self, **_kwargs):
            fig = object()
            ax = _SpyAxes()
            sessions.append(
                {
                    "fig": fig,
                    "ax": ax,
                    "update": None,
                    "frame_returns": [],
                    "frame_snapshots": [],
                }
            )
            return fig, ax

        def show(self):
            current = sessions[-1]
            update_fn = current["update"]
            if update_fn is None:
                raise AssertionError("FuncAnimation was not called before plt.show()")
            for frame in frames:
                ret = update_fn(frame)
                current["frame_returns"].append(ret)
                current["frame_snapshots"].append([a.last_data for a in current["ax"].artists])

    def mock_func_animation(_fig, update_fn, **_kwargs):
        sessions[-1]["update"] = update_fn
        return object()

    stdout_buf = io.StringIO()
    with (
        patch("builtins.input", side_effect=list(inputs)),
        patch("time.sleep"),
        patch("sys.stdout", new=stdout_buf),
        patch.object(module, "plt", _MockPlt()),
        patch.object(module, "FuncAnimation", side_effect=mock_func_animation),
    ):
        result = module.main()

    return {"result": result, "stdout": stdout_buf.getvalue(), "sessions": sessions}


def assert_close_list(actual, expected, tol=1e-9, label="value"):
    if len(actual) != len(expected):
        raise AssertionError(f"{label}: expected length {len(expected)}, got {len(actual)}")
    for idx, (a, e) in enumerate(zip(actual, expected)):
        if not math.isclose(a, e, rel_tol=tol, abs_tol=tol):
            raise AssertionError(f"{label}[{idx}]: expected {e!r}, got {a!r}")


def verify_source_preconditions(target_path: Path):
    lines = target_path.read_text(encoding="utf-8").splitlines()
    required_anchors = {
        15: "def main():",
        46: "if n_harmonics < 1:",
        49: "if n_harmonics > 50:",
        76: "circles = []",
        77: "radii_lines = []",
        134: "return [wave_line, connect_line, drawing_point] + circles + radii_lines",
    }
    for line_no, expected_substr in required_anchors.items():
        if line_no > len(lines) or expected_substr not in lines[line_no - 1]:
            raise AssertionError(
                f"Source anchor mismatch at line {line_no}: expected {expected_substr!r}"
            )
        print(f"[PASS] Source precondition line {line_no}: {expected_substr}")


def verify_case(module, case):
    cid = case["case_id"]
    inputs = list(case["inputs"])
    inputs_before = list(inputs)
    frames = case.get("frames", [])
    expected = case["expected"]

    run = run_case(module, inputs, frames)

    if inputs != inputs_before:
        raise AssertionError(f"{cid}: caller inputs mutated: {inputs!r}")
    if run["result"] is not expected["return_value"]:
        raise AssertionError(
            f"{cid}: expected return {expected['return_value']!r}, got {run['result']!r}"
        )

    for fragment in expected.get("stdout_contains", []):
        if fragment not in run["stdout"]:
            raise AssertionError(f"{cid}: missing stdout fragment {fragment!r}")
    for fragment in expected.get("stdout_excludes", []):
        if fragment in run["stdout"]:
            raise AssertionError(f"{cid}: unexpected stdout fragment {fragment!r}")

    sessions = run["sessions"]
    if len(sessions) != expected["session_count"]:
        raise AssertionError(
            f"{cid}: expected {expected['session_count']} session(s), got {len(sessions)}"
        )

    if expected["session_count"] > 0:
        session = sessions[0]
        ax = session["ax"]
        if ax.title != expected["title"]:
            raise AssertionError(f"{cid}: expected title {expected['title']!r}, got {ax.title!r}")
        if len(ax.artists) != expected["artist_count"]:
            raise AssertionError(
                f"{cid}: expected {expected['artist_count']} artists, got {len(ax.artists)}"
            )

        wave_line, connect_line, drawing_point = ax.artists[:3]
        n_harm = expected["circles_count"]
        circles = [ax.artists[3 + 2 * i] for i in range(n_harm)]
        radii_lines = [ax.artists[3 + 2 * i + 1] for i in range(n_harm)]
        expected_order = [wave_line, connect_line, drawing_point] + circles + radii_lines
        if session["frame_returns"][0] != expected_order:
            raise AssertionError(f"{cid}: update() return ordering mismatch")

        snap0 = session["frame_snapshots"][0]
        assert_close_list(snap0[2][0], [expected["frame0_drawing_point"][0]], label=f"{cid}.f0.x")
        assert_close_list(snap0[2][1], [expected["frame0_drawing_point"][1]], label=f"{cid}.f0.y")

        if 1 in frames:
            snap1 = session["frame_snapshots"][1]
            assert_close_list(
                snap1[2][0], [expected["frame1_drawing_point"][0]], label=f"{cid}.f1.x"
            )
            assert_close_list(
                snap1[2][1], [expected["frame1_drawing_point"][1]], label=f"{cid}.f1.y"
            )
            assert_close_list(snap1[0][0], expected["frame1_wave_x"], label=f"{cid}.f1.wave_x")
            assert_close_list(snap1[0][1], expected["frame1_wave_y"], label=f"{cid}.f1.wave_y")


def main():
    parser = argparse.ArgumentParser(description="Independent checker for R26-T010.")
    parser.add_argument("cases_pos", nargs="?", help="Optional path to cases.json")
    parser.add_argument("--cases", help="Optional path to cases.json")
    parser.add_argument("--target", help="Optional path to target Python module")
    args = parser.parse_args()

    cases_path = Path(args.cases or args.cases_pos or DEFAULT_CASES).resolve()
    target_path = Path(args.target or DEFAULT_TARGET).resolve()

    print("=== R26-T010 Independent Checker ===")
    print(f"Target: {target_path}")
    print(f"Cases:  {cases_path}")

    if not target_path.is_file():
        print(f"[FAIL] Target file not found: {target_path}")
        sys.exit(1)
    if not cases_path.is_file():
        print(f"[FAIL] Cases file not found: {cases_path}")
        sys.exit(1)

    all_passed = True

    print("\n--- Verifying Source Precondition Anchors ---")
    try:
        verify_source_preconditions(target_path)
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Source preconditions: {exc}")

    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    print("\n--- Running Fixture Cases ---")
    for idx, case in enumerate(cases):
        cid = case["case_id"]
        try:
            mod = load_target_module(target_path, f"checker_fourier_{idx}")
            verify_case(mod, case)
            print(f"[PASS] {cid}: {case['description']}")
        except Exception as exc:
            all_passed = False
            print(f"[FAIL] {cid}: {exc}")

    print("\n--- Checking Repeatability Under Controlled External State ---")
    try:
        ord_case = next(c for c in cases if c["case_id"] == "ordinary_input_square_n3")
        mod_a = load_target_module(target_path, "checker_repeat_a")
        mod_b = load_target_module(target_path, "checker_repeat_b")
        run_a = run_case(mod_a, ord_case["inputs"], ord_case["frames"])
        run_b = run_case(mod_b, ord_case["inputs"], ord_case["frames"])
        if run_a["stdout"] != run_b["stdout"]:
            raise AssertionError("Stdout differed across fresh equivalent runs")
        if run_a["sessions"][0]["frame_snapshots"] != run_b["sessions"][0]["frame_snapshots"]:
            raise AssertionError("Frame artist snapshots differed across fresh equivalent runs")
        print("[PASS] Repeatability verified across fresh equivalent inputs.")
    except Exception as exc:
        all_passed = False
        print(f"[FAIL] Repeatability: {exc}")

    print("\n--- Running Focused Pytest Suite ---")
    cmd = [sys.executable, "-m", "pytest", str(TEST_FILE), "-v"]
    print(f"Command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)

    match = re.search(r"(\d+)\s+passed", proc.stdout)
    passed_count = int(match.group(1)) if match else 0
    print(f"Tests passed count: {passed_count}")
    if proc.returncode != 0 or passed_count == 0:
        all_passed = False
        print(f"[FAIL] Pytest failed or zero tests passed (returncode={proc.returncode})")
    else:
        print(f"[PASS] Pytest passed {passed_count} test(s).")

    if not all_passed:
        print("\nONE OR MORE CHECKS FAILED.")
        sys.exit(1)

    print("\nALL R26-T010 CHECKS PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
