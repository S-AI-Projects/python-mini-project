#!/usr/bin/env python3
"""Focused validation checks for the Snake Game and repo tooling.

Each check records its input, expected result, actual result, and tool versions in
work/R26-T022/. A failing assertion exits with a non-zero status.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
REPORT_PATH = OUT_DIR / "check_report.json"
TEXT_REPORT_PATH = OUT_DIR / "check_report.txt"


def _collect_tool_versions() -> dict[str, str]:
    versions: dict[str, str] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
    }
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout or result.stderr or "").strip()
        versions["pytest"] = output or "not installed"
    except Exception as exc:  # pragma: no cover - best effort collection
        versions["pytest"] = f"error: {exc}"
    return versions


def _write_report(results: list[dict[str, Any]], versions: dict[str, str]) -> None:
    payload = {"tool_versions": versions, "checks": results}
    REPORT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["Tool versions:"]
    for key, value in versions.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Checks:")
    for item in results:
        lines.append(f"- {item['name']}: {item['status']}")
        lines.append(f"  input: {json.dumps(item.get('input', {}), sort_keys=True)}")
        lines.append(f"  expected: {json.dumps(item.get('expected', {}), sort_keys=True)}")
        lines.append(f"  actual: {json.dumps(item.get('actual', {}), sort_keys=True)}")
        if item.get("message"):
            lines.append(f"  message: {item['message']}")
    TEXT_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _record_pass(name: str, *, input_data: Any, expected: Any, actual: Any) -> dict[str, Any]:
    return {
        "name": name,
        "status": "pass",
        "input": input_data,
        "expected": expected,
        "actual": actual,
        "message": "",
    }


def _record_fail(name: str, *, input_data: Any, expected: Any, actual: Any, message: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": "fail",
        "input": input_data,
        "expected": expected,
        "actual": actual,
        "message": message,
    }


def _assert_equal(name: str, *, input_data: Any, expected: Any, actual: Any) -> dict[str, Any]:
    if expected == actual:
        return _record_pass(name, input_data=input_data, expected=expected, actual=actual)
    raise AssertionError(f"{name}: expected {expected!r}, got {actual!r} (input={input_data!r})")


def _install_gui_stubs() -> None:
    """Provide headless stubs for turtle/tkinter so the module can import in CI."""
    import types

    if "turtle" not in sys.modules:
        turtle_mod = types.ModuleType("turtle")

        class _DummyTurtle:
            def __init__(self, *args, **kwargs):
                pass

            def __getattr__(self, name):
                def _noop(*_args, **_kwargs):
                    return None
                return _noop

        turtle_mod.Turtle = _DummyTurtle
        turtle_mod.Screen = object
        turtle_mod.Terminator = RuntimeError
        sys.modules["turtle"] = turtle_mod

    if "tkinter" not in sys.modules:
        tkinter_mod = types.ModuleType("tkinter")
        sys.modules["tkinter"] = tkinter_mod

    if "_tkinter" not in sys.modules:
        sys.modules["_tkinter"] = types.ModuleType("_tkinter")


def _load_scoreboard_module():
    _install_gui_stubs()
    module_path = REPO_ROOT / "games" / "Snake-Game" / "scoreboard.py"
    spec = importlib.util.spec_from_file_location("snake_scoreboard", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_scoreboard_boundary_below() -> dict[str, Any]:
    """Score 4 -> increase -> score becomes 5."""
    module = _load_scoreboard_module()
    Scoreboard = module.Scoreboard

    board = Scoreboard()
    board.score = 4
    board.increase()
    return _assert_equal(
        "scoreboard_boundary_below",
        input_data={"starting_score": 4},
        expected={"score": 5, "high_score": 5},
        actual={"score": board.score, "high_score": board.high_score},
    )


def check_scoreboard_boundary_above() -> dict[str, Any]:
    """Score 5 -> increase -> score becomes 6."""
    module = _load_scoreboard_module()
    Scoreboard = module.Scoreboard

    board = Scoreboard()
    board.score = 5
    board.increase()
    return _assert_equal(
        "scoreboard_boundary_above",
        input_data={"starting_score": 5},
        expected={"score": 6, "high_score": 6},
        actual={"score": board.score, "high_score": board.high_score},
    )


def check_pytest_smoke() -> dict[str, Any]:
    """Repo pytest smoke test should pass."""
    command = [sys.executable, "-m", "pytest", "-q", "tests/test_smoke.py"]
    result = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        raise AssertionError(f"pytest smoke check failed: {output}")
    last_line = output.strip().splitlines()[-1] if output.strip() else ""
    return _assert_equal(
        "pytest_smoke",
        input_data={"command": command},
        expected={"exit_code": 0, "last_line": "1 passed in 0.00s"},
        actual={"exit_code": result.returncode, "last_line": last_line},
    )


def run_checks() -> tuple[list[dict[str, Any]], dict[str, str]]:
    versions = _collect_tool_versions()
    results: list[dict[str, Any]] = []
    for check in (check_scoreboard_boundary_below, check_scoreboard_boundary_above, check_pytest_smoke):
        try:
            results.append(check())
        except AssertionError as exc:
            result = _record_fail(
                check.__name__,
                input_data={},
                expected="assertion should pass",
                actual=str(exc),
                message=str(exc),
            )
            results.append(result)
            _write_report(results, versions)
            raise
    return results, versions


def main() -> int:
    try:
        results, versions = run_checks()
    except AssertionError:
        return 1

    _write_report(results, versions)
    print(json.dumps({"tool_versions": versions, "checks": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
