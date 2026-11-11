"""
Focused regression tests for math/Fourier-Series-Visualizer/Fourier-Series-Visualizer.py.

Focus areas tied directly to ``main()`` (line 15):
- Import safety: loading the module causes no stdout/stderr output or GUI/input side effects.
- Smallest valid exit-only session (choice ``"4"``, lines 29-33).
- Smallest valid simulation input (square wave, ``N=1``, lines 35-39, 46, 76-82, 100-102, 134-137).
- Ordinary simulation input (square wave, ``N=3``, lines 63, 76-82, 100-102, 110-134).
- Minimal distinguishing input (square wave, ``N=2``) protecting epicycle coordinate accumulation
  (lines 110-111) and odd-harmonic frequency progression (line 101).
- Sawtooth (lines 103-105) and Triangle (lines 106-108) waveform calculations, including
  negative-radius circle centering via ``abs(radius)`` (lines 115-116).
- Upper harmonic boundary (``N=50``, line 49), invalid-input recovery (lines 35-37, 46-54),
  and the 300-point sliding wave buffer limit (lines 121-123).
- Output type, shape, artist ordering (line 134), input non-mutation, consecutive-session
  isolation, and repeatability under controlled external state.
"""

import importlib.util
import io
import math
import os
from pathlib import Path
import sys
import types
from unittest.mock import patch

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "math"
    / "Fourier-Series-Visualizer"
    / "Fourier-Series-Visualizer.py"
)


class _SimpleArray:
    """Minimal array supporting elementwise scalar multiplication and addition."""

    def __init__(self, values):
        self._values = [float(v) for v in values]

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __getitem__(self, index):
        return self._values[index]

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

    def tolist(self):
        return list(self._values)


def _build_fake_numpy_module():
    """Create a pure-Python fallback shim for numpy when numpy is not installed."""
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


def load_visualizer_module(module_name="fourier_series_visualizer_mod"):
    """Load Fourier-Series-Visualizer.py safely without requiring GUI windows."""
    os.environ.setdefault("MPLBACKEND", "Agg")
    injected_names = []
    saved_modules = {}

    def _inject(name, mod_obj):
        if name in sys.modules:
            saved_modules[name] = sys.modules[name]
        else:
            injected_names.append(name)
        sys.modules[name] = mod_obj

    try:
        import numpy  # noqa: F401
    except ImportError:
        _inject("numpy", _build_fake_numpy_module())

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
        spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec from {MODULE_PATH}")
        module = types.ModuleType(module_name)
        module.__file__ = str(MODULE_PATH)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        for name in injected_names:
            sys.modules.pop(name, None)
        for name, original in saved_modules.items():
            sys.modules[name] = original


class _FakeArtist:
    """Spy Line2D artist capturing initial kwargs and every set_data update."""

    def __init__(self, init_args, init_kwargs):
        self.init_args = init_args
        self.init_kwargs = dict(init_kwargs)
        self.history = []

    def set_data(self, xdata, ydata):
        x_vals = [float(v) for v in xdata]
        y_vals = [float(v) for v in ydata]
        self.history.append((x_vals, y_vals))

    @property
    def last_data(self):
        return self.history[-1] if self.history else None


class _FakeAxes:
    """Spy matplotlib Axes capturing setup calls and created artists in order."""

    def __init__(self):
        self.title = None
        self.xlim = None
        self.ylim = None
        self.aspect = None
        self.grid_call = None
        self.artists = []

    def set_title(self, title):
        self.title = title

    def set_xlim(self, left, right):
        self.xlim = (left, right)

    def set_ylim(self, bottom, top):
        self.ylim = (bottom, top)

    def set_aspect(self, aspect, **kwargs):
        self.aspect = (aspect, dict(kwargs))

    def grid(self, visible, **kwargs):
        self.grid_call = (visible, dict(kwargs))

    def plot(self, *args, **kwargs):
        artist = _FakeArtist(args, kwargs)
        self.artists.append(artist)
        return (artist,)


def _run_main_session(module, user_inputs, frames=(0, 1)):
    """Execute ``module.main()`` with mocked I/O, sleep, and matplotlib GUI."""
    sessions = []
    sleep_calls = []

    class _FakePlt:
        def subplots(self, **kwargs):
            fig = object()
            ax = _FakeAxes()
            sessions.append(
                {
                    "fig": fig,
                    "ax": ax,
                    "subplots_kwargs": dict(kwargs),
                    "animation": None,
                    "frame_returns": [],
                    "frame_snapshots": [],
                }
            )
            return fig, ax

        def show(self):
            current = sessions[-1]
            anim = current["animation"]
            assert anim is not None, "FuncAnimation must be registered before plt.show()"
            update_fn = anim["update"]
            for frame in frames:
                returned = update_fn(frame)
                current["frame_returns"].append(returned)
                current["frame_snapshots"].append(
                    [artist.last_data for artist in current["ax"].artists]
                )

    def fake_func_animation(fig, update_fn, **kwargs):
        current = sessions[-1]
        anim_record = {
            "fig": fig,
            "update": update_fn,
            "kwargs": dict(kwargs),
        }
        current["animation"] = anim_record
        return anim_record

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    captured_stdout = io.StringIO()
    with (
        patch("builtins.input", side_effect=list(user_inputs)),
        patch("time.sleep", side_effect=fake_sleep),
        patch("sys.stdout", new=captured_stdout),
        patch.object(module, "plt", _FakePlt()),
        patch.object(module, "FuncAnimation", side_effect=fake_func_animation),
    ):
        result = module.main()

    return {
        "result": result,
        "stdout": captured_stdout.getvalue(),
        "sleep_calls": sleep_calls,
        "sessions": sessions,
    }


@pytest.fixture
def visualizer_mod():
    return load_visualizer_module("fourier_series_visualizer_test")


def test_import_safety():
    """Importing the module must produce no stdout/stderr and call no input()."""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    with (
        patch("sys.stdout", new=stdout_buf),
        patch("sys.stderr", new=stderr_buf),
        patch("builtins.input") as mock_input,
    ):
        mod = load_visualizer_module("fourier_series_visualizer_import_safety")
        assert callable(getattr(mod, "main", None))
        mock_input.assert_not_called()
    assert stdout_buf.getvalue() == ""
    assert stderr_buf.getvalue() == ""


def test_smallest_valid_exit_only(visualizer_mod):
    """
    Smallest valid CLI session: immediate exit choice ``"4"``.

    Precondition source lines in Fourier-Series-Visualizer.py:
    - Line 15: ``def main():``
    - Line 29: ``choice = input("🎯 Enter choice (1-4): ").strip()``
    - Line 31: ``if choice == "4":`` breaks menu loop and returns ``None``.
    """
    raw_inputs = ["4"]
    original_inputs = list(raw_inputs)
    run = _run_main_session(visualizer_mod, raw_inputs, frames=())

    assert raw_inputs == original_inputs
    assert run["result"] is None
    assert "📈 WELCOME TO FOURIER SERIES VISUALIZER 📈" in run["stdout"]
    assert "👋 Exiting... Keep exploring math!" in run["stdout"]
    assert "Simulating" not in run["stdout"]
    assert run["sleep_calls"] == []
    assert run["sessions"] == []


def test_smallest_valid_simulation_square_n1(visualizer_mod):
    """
    Smallest valid simulation input: square wave with ``N=1`` harmonic, then exit.

    Precondition source lines in Fourier-Series-Visualizer.py:
    - Line 35: ``if choice not in ["1", "2", "3"]:`` accepts ``"1"``
    - Line 39: maps ``"1"`` -> ``"square"``
    - Line 46: ``if n_harmonics < 1:`` establishes ``1`` as smallest valid ``N``
    - Line 49: ``if n_harmonics > 50:`` upper limit respected
    - Line 57: ``time.sleep(0.6)``
    - Lines 63, 66-67: title and axes bounds ``(-3, 10)``, ``(-3, 3)``
    - Lines 72-74: ``wave_line``, ``connect_line``, ``drawing_point``
    - Lines 76-82: ``circles = []`` (line 76) and ``radii_lines = []`` (line 77)
      populated across ``range(n_harmonics)`` (line 78)
    - Lines 84-85: ``time_val = 0``, ``wave_data = []``
    - Lines 100-102: square wave ``n = i * 2 + 1`` (= 1), ``radius = 4 / (n * pi)``
    - Lines 114-129: 50-point circle, radius line, wave buffer, connect line, drawing point
    - Line 131: ``time_val += 0.03``
    - Line 134: ``return [wave_line, connect_line, drawing_point] + circles + radii_lines``
    - Line 136: ``FuncAnimation(fig, update, frames=400, interval=20, blit=True)``
    """
    raw_inputs = ["1", "1", "4"]
    run = _run_main_session(visualizer_mod, raw_inputs, frames=(0, 1))

    assert run["result"] is None
    assert run["sleep_calls"] == [0.6]
    assert "⏳ Simulating square wave with 1 harmonics..." in run["stdout"]
    assert len(run["sessions"]) == 1

    session = run["sessions"][0]
    ax = session["ax"]
    assert session["subplots_kwargs"] == {"figsize": (10, 5)}
    assert ax.title == "Fourier Series Approximation: Square Wave (N=1)"
    assert ax.xlim == (-3, 10)
    assert ax.ylim == (-3, 3)
    assert ax.aspect == ("equal", {"adjustable": "box"})
    assert session["animation"]["kwargs"] == {"frames": 400, "interval": 20, "blit": True}

    # Anchors: [wave_line, connect_line, drawing_point] + circles (1) + radii_lines (1)
    assert len(ax.artists) == 5
    wave_line, connect_line, drawing_point, circle0, radius0 = ax.artists

    returned_f0 = session["frame_returns"][0]
    assert isinstance(returned_f0, list)
    assert returned_f0 == [wave_line, connect_line, drawing_point, circle0, radius0]

    # Hand-calculated frame 0 (time_val = 0): r0 = 4 / pi = 1.2732395447351628
    snap0 = session["frame_snapshots"][0]
    assert snap0[0][0] == pytest.approx([3.0])
    assert snap0[0][1] == pytest.approx([0.0])
    assert snap0[1][0] == pytest.approx([1.2732395447351628, 3.0])
    assert snap0[1][1] == pytest.approx([0.0, 0.0])
    assert snap0[2][0] == pytest.approx([1.2732395447351628])
    assert snap0[2][1] == pytest.approx([0.0])
    assert len(snap0[3][0]) == 50
    assert len(snap0[3][1]) == 50
    assert snap0[3][0][0] == pytest.approx(1.2732395447351628)
    assert snap0[3][1][0] == pytest.approx(0.0)
    assert snap0[3][0][-1] == pytest.approx(1.2732395447351628)
    assert snap0[3][1][-1] == pytest.approx(0.0, abs=1e-12)
    assert snap0[4][0] == pytest.approx([0.0, 1.2732395447351628])
    assert snap0[4][1] == pytest.approx([0.0, 0.0])

    # Hand-calculated frame 1 (time_val = 0.03):
    # x1 = (4/pi)*cos(0.03) = 1.2726666299105776, y1 = (4/pi)*sin(0.03) = 0.038191457021929054
    snap1 = session["frame_snapshots"][1]
    assert snap1[0][0] == pytest.approx([3.0, 3.06])
    assert snap1[0][1] == pytest.approx([0.038191457021929054, 0.0])
    assert snap1[1][0] == pytest.approx([1.2726666299105776, 3.0])
    assert snap1[1][1] == pytest.approx([0.038191457021929054, 0.038191457021929054])
    assert snap1[2][0] == pytest.approx([1.2726666299105776])
    assert snap1[2][1] == pytest.approx([0.038191457021929054])
    assert snap1[4][0] == pytest.approx([0.0, 1.2726666299105776])
    assert snap1[4][1] == pytest.approx([0.0, 0.038191457021929054])


def test_ordinary_input_square_n3(visualizer_mod):
    """
    Ordinary simulation input: square wave with ``N=3`` harmonics, then exit.

    Precondition source lines in Fourier-Series-Visualizer.py:
    - Line 46 & 49: ``1 <= 3 <= 50`` interior harmonic count
    - Lines 76-82: ``circles = []`` (line 76) and ``radii_lines = []`` (line 77)
      grow to length 3 via alternating ``ax.plot`` calls inside ``for _ in range(3):``
    - Lines 101-102: odd harmonics ``n = 1, 3, 5`` with radii ``4/pi, 4/(3*pi), 4/(5*pi)``
    - Lines 110-111: ``x += radius * math.cos(n * time_val)`` and ``y += radius * math.sin(n * time_val)``
    - Line 121: ``wave_data.insert(0, y)`` (newest sample first)
    - Line 134: ``return [wave_line, connect_line, drawing_point] + circles + radii_lines``
    """
    run = _run_main_session(visualizer_mod, ["1", "3", "4"], frames=(0, 1))
    assert run["result"] is None
    assert len(run["sessions"]) == 1

    session = run["sessions"][0]
    ax = session["ax"]
    assert ax.title == "Fourier Series Approximation: Square Wave (N=3)"
    assert len(ax.artists) == 9

    wave_line, connect_line, drawing_point = ax.artists[:3]
    circles = [ax.artists[3], ax.artists[5], ax.artists[7]]
    radii_lines = [ax.artists[4], ax.artists[6], ax.artists[8]]
    expected_return = [wave_line, connect_line, drawing_point] + circles + radii_lines
    assert session["frame_returns"][0] == expected_return

    # Frame 0 (time_val = 0):
    # Partial sums: 4/pi = 1.2732395447351628,
    # 16/(3*pi) = 1.6976527263135504, 92/(15*pi) = 1.952300635260583
    snap0 = session["frame_snapshots"][0]
    assert snap0[2][0] == pytest.approx([1.952300635260583])
    assert snap0[2][1] == pytest.approx([0.0])
    assert snap0[4][0] == pytest.approx([0.0, 1.2732395447351628])
    assert snap0[6][0] == pytest.approx([1.2732395447351628, 1.6976527263135504])
    assert snap0[8][0] == pytest.approx([1.6976527263135504, 1.952300635260583])

    # Frame 1 (time_val = 0.03):
    # x = 1.9471505854536049, y = 0.11439120599405823
    snap1 = session["frame_snapshots"][1]
    assert snap1[0][0] == pytest.approx([3.0, 3.06])
    assert snap1[0][1] == pytest.approx([0.11439120599405823, 0.0])
    assert snap1[1][0] == pytest.approx([1.9471505854536049, 3.0])
    assert snap1[1][1] == pytest.approx([0.11439120599405823, 0.11439120599405823])
    assert snap1[2][0] == pytest.approx([1.9471505854536049])
    assert snap1[2][1] == pytest.approx([0.11439120599405823])


def test_minimal_distinguishing_input_square_n2_accumulation(visualizer_mod):
    """
    Reduced valid input ``["1", "2", "4"]`` distinguishing accumulation and frequency defects.

    Protects:
    - Line 110: ``x += radius * math.cos(n * time_val)`` (vs overwriting ``x = ...``)
    - Line 111: ``y += radius * math.sin(n * time_val)`` (vs overwriting ``y = ...``)
    - Line 101: ``n = i * 2 + 1`` (vs ``n = i + 1`` which gives n=2 instead of n=3)
    """
    run = _run_main_session(visualizer_mod, ["1", "2", "4"], frames=(0, 1))
    session = run["sessions"][0]

    # Frame 0: 4/pi + 4/(3*pi) = 16/(3*pi) = 1.6976527263135504
    snap0 = session["frame_snapshots"][0]
    assert snap0[2][0] == pytest.approx([1.6976527263135504])
    assert snap0[2][1] == pytest.approx([0.0])

    # Frame 1 (time_val = 0.03):
    # x = (4/pi)*cos(0.03) + (4/(3*pi))*cos(0.09) = 1.6953620980298885
    # y = (4/pi)*sin(0.03) + (4/(3*pi))*sin(0.09) = 0.07633709804270655
    snap1 = session["frame_snapshots"][1]
    assert snap1[2][0] == pytest.approx([1.6953620980298885])
    assert snap1[2][1] == pytest.approx([0.07633709804270655])


def test_sawtooth_and_triangle_waveforms(visualizer_mod):
    """
    Verify Sawtooth (lines 103-105) and Triangle (lines 106-108) series formulas.
    """
    saw_run = _run_main_session(visualizer_mod, ["2", "2", "4"], frames=(0, 1))
    saw_session = saw_run["sessions"][0]
    assert saw_session["ax"].title == "Fourier Series Approximation: Sawtooth Wave (N=2)"
    # Frame 0: 2/pi - 1/pi = 1/pi = 0.3183098861837907; circle[1] uses abs(-1/pi) at center 2/pi
    saw_snap0 = saw_session["frame_snapshots"][0]
    assert saw_snap0[2][0] == pytest.approx([0.3183098861837907])
    assert saw_snap0[2][1] == pytest.approx([0.0])
    assert saw_snap0[5][0][0] == pytest.approx(0.954929658551372)
    assert saw_snap0[6][0] == pytest.approx([0.6366197723675814, 0.3183098861837907])
    # Frame 1 (time_val = 0.03):
    saw_snap1 = saw_session["frame_snapshots"][1]
    assert saw_snap1[2][0] == pytest.approx([0.3185962146999155])
    assert saw_snap1[2][1] == pytest.approx([8.592433368429658e-06])

    tri_run = _run_main_session(visualizer_mod, ["3", "2", "4"], frames=(0, 1))
    tri_session = tri_run["sessions"][0]
    assert tri_session["ax"].title == "Fourier Series Approximation: Triangle Wave (N=2)"
    # Frame 0: 8/pi^2 - 8/(9*pi^2) = 64/(9*pi^2) = 0.7205061947899575
    tri_snap0 = tri_session["frame_snapshots"][0]
    assert tri_snap0[2][0] == pytest.approx([0.7205061947899575])
    assert tri_snap0[2][1] == pytest.approx([0.0])
    # Frame 1 (time_val = 0.03):
    tri_snap1 = tri_session["frame_snapshots"][1]
    assert tri_snap1[2][0] == pytest.approx([0.7205059760018473])
    assert tri_snap1[2][1] == pytest.approx([0.01621868024119913])


def test_upper_boundary_n50_and_invalid_input_recovery(visualizer_mod):
    """
    Upper harmonic boundary (N=50, line 49) and menu/harmonic input validation recovery.

    Precondition source lines in Fourier-Series-Visualizer.py:
    - Lines 35-37: invalid menu choices print warning and reprompt
    - Lines 46-48: ``n_harmonics < 1`` prints warning and reprompt
    - Lines 49-51: ``n_harmonics > 50`` prints warning and reprompt; ``50`` is accepted
    - Lines 53-54: non-numeric input catches ``ValueError`` and reprompt
    """
    upper_run = _run_main_session(visualizer_mod, ["1", "50", "4"], frames=(0,))
    upper_session = upper_run["sessions"][0]
    assert upper_session["ax"].title == "Fourier Series Approximation: Square Wave (N=50)"
    assert len(upper_session["ax"].artists) == 103
    assert len(upper_session["frame_returns"][0]) == 103

    recovery_inputs = ["0", "5", "abc", "1", "0", "51", "bad", "1", "4"]
    recovery_run = _run_main_session(visualizer_mod, recovery_inputs, frames=(0,))
    assert recovery_run["stdout"].count("❌ Invalid choice. Please pick 1, 2, 3, or 4.") == 3
    assert "⚠️ Enter a value greater than or equal to 1." in recovery_run["stdout"]
    assert "⚠️ For performance, keep harmonics up to 50." in recovery_run["stdout"]
    assert "⚠️ Invalid number. Try again." in recovery_run["stdout"]
    assert "⏳ Simulating square wave with 1 harmonics..." in recovery_run["stdout"]
    assert len(recovery_run["sessions"]) == 1


def test_wave_data_sliding_window_caps_at_300(visualizer_mod):
    """
    Verify ``wave_data`` caps at 300 entries (lines 121-123: ``if len(wave_data) > 300:``).
    """
    run = _run_main_session(visualizer_mod, ["1", "1", "4"], frames=range(301))
    session = run["sessions"][0]
    snap_300 = session["frame_snapshots"][299]
    snap_301 = session["frame_snapshots"][300]

    assert len(snap_300[0][0]) == 300
    assert len(snap_300[0][1]) == 300
    assert len(snap_301[0][0]) == 300
    assert len(snap_301[0][1]) == 300
    assert snap_301[0][0][0] == pytest.approx(3.0)
    assert snap_301[0][0][-1] == pytest.approx(12.0)


def test_repeatability_and_session_isolation(visualizer_mod):
    """
    Compare fresh equivalent inputs under controlled external state and verify
    consecutive simulations in one ``main()`` loop do not leak state.
    """
    inputs_a = ["1", "3", "4"]
    inputs_b = ["1", "3", "4"]
    inputs_b_copy = list(inputs_b)

    run_a = _run_main_session(
        load_visualizer_module("fourier_repeat_a"), inputs_a, frames=(0, 1)
    )
    run_b = _run_main_session(
        load_visualizer_module("fourier_repeat_b"), inputs_b, frames=(0, 1)
    )

    assert inputs_b == inputs_b_copy
    assert run_a["result"] is None and run_b["result"] is None
    assert run_a["stdout"] == run_b["stdout"]
    assert run_a["sessions"][0]["ax"].title == run_b["sessions"][0]["ax"].title
    assert run_a["sessions"][0]["frame_snapshots"] == run_b["sessions"][0]["frame_snapshots"]

    # Consecutive runs in one main() invocation: Square N=3 followed by Sawtooth N=1
    multi_run = _run_main_session(visualizer_mod, ["1", "3", "2", "1", "4"], frames=(0, 1))
    assert len(multi_run["sessions"]) == 2
    second_session = multi_run["sessions"][1]
    assert second_session["ax"].title == "Fourier Series Approximation: Sawtooth Wave (N=1)"
    assert len(second_session["ax"].artists) == 5
    # time_val reset to 0 on second session -> frame 0 y must be 0.0 and x = 2/pi
    assert second_session["frame_snapshots"][0][2][0] == pytest.approx([0.6366197723675814])
    assert second_session["frame_snapshots"][0][2][1] == pytest.approx([0.0])
