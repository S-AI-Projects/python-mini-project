#!/usr/bin/env python3
"""Focused independent checker for R26-T008: Cover Caesar Cipher failure behavior."""

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "utilities" / "Caesar-Cipher" / "Caesar-Cipher.py"
CASES_FILE = Path(__file__).resolve().parent / "cases.json"
TEST_FILE = REPO_ROOT / "tests" / "test_caesar_cipher.py"


def main():
    print("=== Running R26-T008 Independent Checker ===")

    # 1. Load target module dynamically
    spec = importlib.util.spec_from_file_location("caesar_cipher_module", TARGET_FILE)
    if spec is None or spec.loader is None:
        print("[FAIL] Could not load spec for Caesar-Cipher.py")
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    caesar_cipher = getattr(mod, "caesar_cipher", None)
    if not callable(caesar_cipher):
        print("[FAIL] caesar_cipher function not found in module")
        sys.exit(1)

    # 2. Verify all fixtures from cases.json
    print("--- Verifying Required Fixtures from cases.json ---")
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    for case in cases:
        msg = case["message"]
        shift = case["shift"]
        mode = case["mode"]
        exp = case["expected"]
        res = caesar_cipher(msg, shift, mode)
        if res != exp:
            print(f"[FAIL] Case {case['id']} ({case['description']}): expected {exp!r}, got {res!r}")
            sys.exit(1)
        print(f"[PASS] Case {case['id']}: {case['description']} -> {res!r}")

    # 3. Verify caller-owned input integrity and subsequent valid call
    print("--- Verifying Caller Input Integrity and Subsequent Valid Call ---")
    original = "abc"
    res_empty = caesar_cipher("", 3, "E")
    if res_empty != "":
        print(f"[FAIL] Empty input expected '', got {res_empty!r}")
        sys.exit(1)

    res_valid = caesar_cipher(original, 3, "E")
    if res_valid != "def":
        print(f"[FAIL] Subsequent valid call expected 'def', got {res_valid!r}")
        sys.exit(1)

    if original != "abc":
        print(f"[FAIL] Original input string mutated: expected 'abc', got {original!r}")
        sys.exit(1)
    print("[PASS] Caller input string preserved and subsequent call succeeded.")

    # 4. Run pytest suite and propagate result
    print("--- Running Pytest Suite ---")
    cmd = ["python3", "-m", "pytest", str(TEST_FILE), "-v"]
    print(f"Command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)

    match = re.search(r"(\d+)\s+passed", proc.stdout)
    passed_count = int(match.group(1)) if match else 0
    print(f"Tests passed count: {passed_count}")

    if proc.returncode != 0 or passed_count == 0:
        print(f"[FAIL] Pytest failed or 0 tests passed (code={proc.returncode})")
        sys.exit(1)

    print("\nALL R26-T008 CHECKS PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
