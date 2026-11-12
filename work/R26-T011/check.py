
import json
import os
import sys
import io
import tempfile
import importlib.util
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

# Project paths
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "utilities" / "Progress-Tracker" / "Progress-Tracker.py"
EVIDENCE = Path(__file__).resolve().parent

# Registry fixture: source lines 16-26 define categories and mappings.
REGISTRY = [
    {"category": "games", "path": "Games/Rolling-Dice/main.py"},
    {"category": "games", "path": "Games/Flipping-Toss/main.py"},
    {"category": "math", "path": "Math/Pascal-Triangle/main.py"},
    {"category": "games", "path": "Games/Snake-Game/main.py"},
    {"category": "games", "path": "Games/Chess/main.py"},
]


def load_module():
    """Import only the Progress Tracker module with registry I/O mocked."""

    if not SOURCE.exists():
        raise FileNotFoundError(f"Source file not found: {SOURCE}")

    spec = importlib.util.spec_from_file_location(
        "progress_tracker", SOURCE
    )
    module = importlib.util.module_from_spec(spec)

    registry_path = os.path.abspath(
        SOURCE.parent.parent.parent / "projects_registry.json"
    )

    original_open = open

    def mocked_open(file, *args, **kwargs):
        try:
            path = os.path.abspath(os.fspath(file))
        except TypeError:
            path = None

        if path == registry_path:
            return io.StringIO(json.dumps(REGISTRY))

        return original_open(file, *args, **kwargs)

    with patch("builtins.open", side_effect=mocked_open):
        spec.loader.exec_module(module)

    return module


tracker = load_module()

# Every case records its source anchor and independently calculated result.
CASES = [
    {
        "name": "Missing JSON file",
        "source_anchor": "Progress-Tracker.py:48-50, 78-79",
        "input": None,
        "expected": {"completed": {}},
        "expected_file": None,
    },
    {
        "name": "Smallest valid input",
        "source_anchor": "Progress-Tracker.py:59-61, 78",
        "input": {"completed": {}},
        "expected": {"completed": {}},
        "expected_file": {"completed": {}},
    },
    {
        "name": "Ordinary project data",
        "source_anchor": "Progress-Tracker.py:59-74",
        "input": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00"
            }
        },
        "expected": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00"
            }
        },
        "expected_file": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00"
            }
        },
    },
    {
        "name": "Repeated timestamp values",
        "source_anchor": "Progress-Tracker.py:62-74",
        "input": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00",
                "Chess": "2026-11-01 10:00"
            }
        },
        "expected": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00",
                "Chess": "2026-11-01 10:00"
            }
        },
        "expected_file": {
            "completed": {
                "Snake-Game": "2026-11-01 10:00",
                "Chess": "2026-11-01 10:00"
            }
        },
    },
    {
        "name": "Valid old project name migration",
        "source_anchor": "Progress-Tracker.py:54-68, 75-78",
        "input": {
            "completed": {
                "Dice-Rolling": "2026-11-01 10:00"
            }
        },
        "expected": {
            "completed": {
                "Rolling-Dice": "2026-11-01 10:00"
            }
        },
        "expected_file": {
            "completed": {
                "Rolling-Dice": "2026-11-01 10:00"
            }
        },
    },
]


def run_case(case):
    """Run one test using a temporary JSON file."""

    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = Path(temp_dir) / "completed_projects.json"

        # Prepare input.
        if case["input"] is not None:
            data_file.write_text(
                json.dumps(case["input"], indent=2),
                encoding="utf-8"
            )

        # Redirect the module's data file to our temporary file.
        tracker.DATA_FILE = str(data_file)

        output = io.StringIO()

        with redirect_stdout(output):
            actual_return = tracker.load_data()

        # Read actual persisted file state.
        if data_file.exists():
            actual_file = json.loads(
                data_file.read_text(encoding="utf-8")
            )
        else:
            actual_file = None

        # Check returned value separately from file mutation.
        return_ok = actual_return == case["expected"]
        file_ok = actual_file == case["expected_file"]

        return {
            "name": case["name"],
            "source_anchor": case["source_anchor"],
            "input": case["input"],
            "expected_return": case["expected"],
            "actual_return": actual_return,
            "expected_file": case["expected_file"],
            "actual_file": actual_file,
            "return_pass": return_ok,
            "file_pass": file_ok,
            "stdout": output.getvalue(),
        }


def main():
    results = []

    for case in CASES:
        result = run_case(case)
        results.append(result)

        status = (
            "PASS"
            if result["return_pass"] and result["file_pass"]
            else "FAIL"
        )

        print(f"[{status}] {result['name']}")
        print(f"  Source: {result['source_anchor']}")
        print(f"  Expected: {result['expected_return']}")
        print(f"  Actual:   {result['actual_return']}")
        print(f"  File mutation: {'PASS' if result['file_pass'] else 'FAIL'}")
        print()

    passed = sum(
        1 for r in results
        if r["return_pass"] and r["file_pass"]
    )
    failed = len(results) - passed

    # Save required evidence.
    (EVIDENCE / "inputs.json").write_text(
        json.dumps(
            [{"name": r["name"], "input": r["input"]}
             for r in results],
            indent=2
        ),
        encoding="utf-8"
    )

    (EVIDENCE / "expected.json").write_text(
        json.dumps(
            [{"name": r["name"],
              "return": r["expected_return"],
              "file": r["expected_file"]}
             for r in results],
            indent=2
        ),
        encoding="utf-8"
    )

    (EVIDENCE / "actual.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    summary = (
        "Progress Tracker load_data contract checks\n"
        f"Command: python3 work/R26-T011/check.py\n"
        f"Python version: {sys.version}\n"
        f"Total checks: {len(results)}\n"
        f"Passed: {passed}\n"
        f"Failed: {failed}\n"
    )

    (EVIDENCE / "results.txt").write_text(
        summary,
        encoding="utf-8"
    )

    print("=" * 45)
    print(summary)

    if failed:
        print("Some checks failed. Review actual.json.")
        return 1

    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
