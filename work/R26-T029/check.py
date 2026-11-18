import subprocess
import sys
import xml.etree.ElementTree as ET
import json
import platform
import random
import statistics
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEST_FILE = Path(__file__).resolve().parent / "test_fibonacci_series.py"
OUTPUT_DIR = Path(__file__).resolve().parent
RESULTS_FILE = OUTPUT_DIR / "results.json"
CASE_RESULTS_FILE = OUTPUT_DIR / "case-results.jsonl"


def load_named_module():
    import importlib.util
    import sys as local_sys
    from types import ModuleType
    from unittest.mock import patch

    module_path = ROOT / "math" / "Fibonacci-Series" / "Fibonacci-Series.py"
    turtle = ModuleType("turtle")
    with patch.dict(local_sys.modules, {"turtle": turtle}):
        spec = importlib.util.spec_from_file_location("fibonacci_series_native_check", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    return module


def count_nonzero_tests(xml_path: Path) -> int:
    if not xml_path.exists():
        return 0

    root = ET.parse(xml_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    return failures + errors


def junit_test_count(xml_path: Path) -> int:
    if not xml_path.exists():
        return 0
    root = ET.parse(xml_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    return sum(int(suite.attrib.get("tests", 0)) for suite in suites)


def run_benchmark(module) -> list[dict]:
    sizes = (100, 1_000, 10_000)
    repetitions = 5
    random.seed(20261118)
    records = []

    for n in sizes:
        timings_us = []
        fresh_inputs = []

        for _ in range(repetitions):
            fresh_n = n
            random.randint(0, 1_000_000)
            fresh_inputs.append(fresh_n)

            start = time.perf_counter_ns()
            actual = module.generate_fibonacci(fresh_n)
            elapsed_ns = time.perf_counter_ns() - start

            assert isinstance(actual, list), f"n={fresh_n}: result must be a list"
            assert len(actual) == fresh_n, f"n={fresh_n}: incorrect result length"
            assert actual[0] == 1, f"n={fresh_n}: first term mismatch"
            if fresh_n >= 2:
                assert actual[1] == 1, f"n={fresh_n}: second term mismatch"
                assert all(
                    actual[i] == actual[i - 1] + actual[i - 2]
                    for i in range(2, fresh_n)
                ), f"n={fresh_n}: Fibonacci recurrence mismatch"

            timings_us.append(elapsed_ns / 1_000)

        records.append({
            "check": "generate_fibonacci_benchmark",
            "inputs": {
                "n": n,
                "seed": 20261118,
                "repetitions": repetitions,
                "fresh_inputs": fresh_inputs,
            },
            "expected": {
                "result_length": n,
                "median_status": "measured",
                "range_status": "measured",
            },
            "actual": {
                "median_us": round(statistics.median(timings_us), 3),
                "range_us": [
                    round(min(timings_us), 3),
                    round(max(timings_us), 3),
                ],
            },
            "status": "passed",
            "message": None,
        })

    return records


def main() -> int:
    junit_xml = OUTPUT_DIR / "pytest-results.xml"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-c",
        str(ROOT / "pyproject.toml"),
        "-q",
        f"--junitxml={junit_xml}",
        str(TEST_FILE),
    ]

    print("Native check command:", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)

    nonzero_test_count = count_nonzero_tests(junit_xml)
    test_count = junit_test_count(junit_xml)

    try:
        benchmark_module = load_named_module()
        benchmark_records = run_benchmark(benchmark_module)
        benchmark_status = "passed"
        benchmark_error = None
    except AssertionError as error:
        benchmark_records = [{
            "check": "generate_fibonacci_benchmark",
            "inputs": {"seed": 20261118},
            "expected": {"result_validation": "pass"},
            "actual": {"result_validation": "fail"},
            "status": "failed",
            "message": str(error),
        }]
        benchmark_status = "failed"
        benchmark_error = str(error)

    try:
        import pytest
        pytest_version = pytest.__version__
    except ImportError:
        pytest_version = "not installed"

    case_records = list(benchmark_records)
    for n, expected in [
        (0, []),
        (-3, []),
        (1, [1]),
        (2, [1, 1]),
        (10, [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]),
    ]:
        actual = benchmark_module.generate_fibonacci(n)
        case_records.append({
            "check": "generate_fibonacci",
            "inputs": {"term_count": n},
            "expected": expected,
            "actual": actual,
            "status": "passed" if actual == expected else "failed",
            "message": None,
        })

    failed_cases = [record for record in case_records if record["status"] != "passed"]
    with CASE_RESULTS_FILE.open("w", encoding="utf-8") as handle:
        for record in case_records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    results = {
        "command": " ".join(command),
        "working_directory": str(ROOT),
        "tool_versions": {
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "platform": f"{platform.system()}-{platform.release()}-{platform.machine()}",
            "pytest": pytest_version,
        },
        "test_count": test_count,
        "test_results": [
            {
                "name": "focused_fibonacci_suite",
                "status": "passed" if result.returncode == 0 else "failed",
                "message": None,
            }
        ],
        "nonzero_test_count": nonzero_test_count,
        "benchmark_status": benchmark_status,
        "benchmark_error": benchmark_error,
        "case_results_file": CASE_RESULTS_FILE.name,
        "case_count": len(case_records),
        "pytest_results_file": junit_xml.name,
        "pytest_exit_code": result.returncode,
    }
    RESULTS_FILE.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    print(f"Test count: {test_count}")
    print(f"Nonzero test count: {nonzero_test_count}")
    print(f"Benchmark status: {benchmark_status}")

    if result.returncode != 0:
        return result.returncode
    if nonzero_test_count != 0:
        return 1
    if benchmark_status != "passed":
        return 1
    if failed_cases:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
