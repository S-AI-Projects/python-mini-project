#!/usr/bin/env python3
"""Focused validation runner for the project.

This script runs the repository's pytest configuration against the most relevant
small test target and then exercises a specific module in isolation with mocked
external I/O. It exits non-zero if either stage fails so CI can propagate the
failure immediately.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shlex
import subprocess
import sys
import types
from pathlib import Path
from typing import Iterable
from unittest.mock import mock_open, patch


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    repo_root = resolve_repo_root()
    parser = argparse.ArgumentParser(
        description="Run focused project tests and a mocked import/invocation for a target module."
    )
    parser.add_argument(
        "--module",
        default="math/Happy-Number/Happy-Number.py",
        help="Path to the Python module under test, relative to the repo root.",
    )
    parser.add_argument(
        "--tests",
        nargs="*",
        default=["tests/test_smoke.py"],
        help="Focused pytest target(s). Defaults to a minimal smoke test.",
    )
    parser.add_argument(
        "--call",
        default="is_happy_number",
        help="Function to invoke inside the module once it has been imported. Defaults to is_happy_number.",
    )
    parser.add_argument(
        "--call-args",
        default="7,2",
        help="Comma-separated positional arguments to pass to the invocation target. Empty string means no args.",
    )
    parser.add_argument(
        "--pytest-args",
        default="-q --maxfail=1",
        help="Extra pytest flags to append. Defaults to a focused single-failure run.",
    )
    parser.add_argument(
        "--no-module-check",
        action="store_true",
        help="Skip the isolated module invocation stage.",
    )
    return parser.parse_args()


def build_pytest_command(repo_root: Path, tests: Iterable[str], extra_args: str) -> list[str]:
    cmd = [sys.executable, "-m", "pytest"]
    cmd.extend(str(test) for test in tests)
    if extra_args.strip():
        cmd.extend(extra_args.split())
    return cmd


def extract_nonzero_test_count(output: str) -> int:
    """Return the number of failed/error tests reported by pytest.

    We intentionally only count failing/error states; skipped or xpassed tests do
    not make a focused run fail for project validation purposes.
    """
    failed = 0
    errors = 0
    for label, count in re.findall(r"(\d+)\s+(failed|error|errors)", output, flags=re.IGNORECASE):
        if label:
            if label.lower().endswith("error"):
                errors += int(label)
            else:
                failed += int(label)
    return failed + errors


def run_pytest(repo_root: Path, tests: Iterable[str], extra_args: str) -> int:
    cmd = build_pytest_command(repo_root, tests, extra_args)
    print(f"Command: {shlex.join(cmd)}")
    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    output = f"{proc.stdout}{proc.stderr}"
    if output:
        print(output, end="")
    nonzero_count = extract_nonzero_test_count(output)
    print(f"Non-zero tests: {nonzero_count}")
    if proc.returncode != 0 or nonzero_count > 0:
        return 1
    return 0


def load_module(module_path: Path):
    if not module_path.exists():
        raise FileNotFoundError(f"Module not found: {module_path}")

    module_name = module_path.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create a module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)

    # Some repository modules import GUI libraries at module scope. The project
    # test environment is headless, so stub the GUI layer to keep the import
    # isolated and deterministic for native validation checks.
    tkinter_stub = types.ModuleType("tkinter")
    tkinter_stub.Tk = type("TkStub", (), {"__init__": lambda self, *a, **k: None})
    tkinter_stub.Frame = type("Frame", (), {})
    tkinter_stub.Scrollbar = type("Scrollbar", (), {})
    tkinter_stub.Canvas = type("Canvas", (), {})
    tkinter_stub.LAST = "last"
    tkinter_stub.ALL = "all"

    sys.modules.setdefault("tkinter", tkinter_stub)
    module.__dict__.setdefault("__builtins__", __builtins__)
    spec.loader.exec_module(module)
    return module


def parse_call_args(raw_args: str):
    if not raw_args or not raw_args.strip():
        return ()
    values = []
    for chunk in raw_args.split(","):
        item = chunk.strip()
        if not item:
            continue
        if item.lower() in {"true", "false"}:
            values.append(item.lower() == "true")
        else:
            try:
                values.append(int(item))
            except ValueError:
                values.append(item)
    return tuple(values)


def invoke_module(module_path: Path, call_name: str, call_args: str) -> None:
    module = load_module(module_path)
    target = getattr(module, call_name)
    result = target(*parse_call_args(call_args))
    print(f"Module invocation: {call_name}{tuple(parse_call_args(call_args))} -> {result}")


def smoke_module(module_path: Path) -> None:
    """A small import-time smoke check that exercises a function with mocked I/O.

    This keeps the check isolated from any real stdin/stdout or file-system side effects.
    """
    module = load_module(module_path)

    if hasattr(module, "is_happy_number"):
        happy = module.is_happy_number(7)
        unhappy = module.is_happy_number(2)
        if happy[0] is not True:
            raise AssertionError("Expected 7 to be happy")
        if unhappy[0] is not False:
            raise AssertionError("Expected 2 to be unhappy")
        print("Module smoke check: is_happy_number(7) == True; is_happy_number(2) == False")
        return

    if hasattr(module, "main"):
        with patch("builtins.input", side_effect=["7", "n"]), patch("sys.stdin"), patch("sys.stdout"):
            module.main()
        print("Module smoke check: main() exited after a mocked interactive session")
        return

    raise AttributeError(f"No importable callable smoke target found in {module_path}")


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root()
    module_path = (repo_root / args.module).resolve()

    pytest_rc = run_pytest(repo_root, args.tests, args.pytest_args)
    if pytest_rc != 0:
        return pytest_rc

    if not args.no_module_check:
        try:
            smoke_module(module_path)
        except Exception as exc:  # noqa: BLE001 - fail the native check clearly
            print(f"Module smoke check failed: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
