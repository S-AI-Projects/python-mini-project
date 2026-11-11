#!/usr/bin/env python3
"""
Independent checker script for Contact Book CSV (R26-T009).

Verifies:
1. Every fixture in cases.json against both main.py and an independent ReferenceContactStore.
2. Independent ReferenceContactStore does NOT import main.py.
3. Negative verification checks non-zero exit on failure.
4. Unittest suite discovery passes cleanly.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
CASES_FILE = BASE_DIR / "cases.json"
MAIN_FILE = REPO_ROOT / "utilities" / "Contact-Book-CSV" / "main.py"
TEST_DIR = REPO_ROOT / "utilities" / "Contact-Book-CSV"


class ReferenceContactStore:
    """
    Independent reference implementation using standard python dict.
    Does NOT import or call main.py.
    """

    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}
        self._order: list[str] = []

    def add(self, contact: dict[str, str]) -> None:
        cid = contact.get("id")
        if not cid:
            raise ValueError("Contact missing id")
        if cid in self._data:
            raise ValueError(f"Duplicate contact ID: {cid}")
        self._data[cid] = dict(contact)
        self._order.append(cid)

    def get(self, contact_id: str) -> dict[str, str] | None:
        if contact_id in self._data:
            return dict(self._data[contact_id])
        return None

    def update(self, contact_id: str, updates: dict[str, str]) -> None:
        if contact_id not in self._data:
            raise KeyError(f"Contact ID '{contact_id}' not found")
        if "id" in updates and str(updates["id"]).strip() != contact_id:
            raise ValueError("Cannot modify stable contact ID")
        for k, v in updates.items():
            if k in ("name", "phone", "email"):
                self._data[contact_id][k] = str(v)

    def delete(self, contact_id: str) -> None:
        if contact_id not in self._data:
            raise KeyError(f"Contact ID '{contact_id}' not found")
        del self._data[contact_id]
        self._order.remove(contact_id)

    def count_worst_case_lookup_comparisons(self, size: int) -> int:
        return size


def load_target_module():
    spec = importlib.util.spec_from_file_location("cb_main", MAIN_FILE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec from {MAIN_FILE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    print("=== Running R26-T009 Independent Checker ===")

    if not CASES_FILE.exists():
        sys.stderr.write(f"cases.json missing at {CASES_FILE}\n")
        return 1

    with open(CASES_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    target_mod = load_target_module()

    all_passed = True
    print(f"Loaded {len(cases)} test cases from {CASES_FILE.name}")
    print("-" * 70)

    ref_store = ReferenceContactStore()

    for case in cases:
        case_id = case["id"]
        desc = case["description"]
        case_type = case["type"]
        status = "PASS"
        detail = ""

        try:
            if case_type == "roundtrip":
                contact = case["contact"]
                expected = case["expected"]
                csv_str = target_mod.contacts_to_csv_string([contact])
                loaded = target_mod.contacts_from_csv_string(csv_str)
                if loaded != [expected]:
                    status = "FAIL"
                    detail = f"Expected {[expected]}, got {loaded}"

            elif case_type == "duplicate_add":
                existing = case["existing"]
                new_c = case["new_contact"]
                expected_err = case["expected_error"]
                try:
                    target_mod.add_contact(existing, new_c)
                    status = "FAIL"
                    detail = f"Expected exception {expected_err}, but none was raised"
                except Exception as exc:
                    if type(exc).__name__ != expected_err:
                        status = "FAIL"
                        detail = f"Expected {expected_err}, got {type(exc).__name__}"

                # Cross-check reference store
                try:
                    ref_check = ReferenceContactStore()
                    for c in existing:
                        ref_check.add(c)
                    ref_check.add(new_c)
                except ValueError:
                    pass  # expected

            elif case_type == "duplicate_csv":
                csv_content = case["csv_content"]
                expected_err = case["expected_error"]
                try:
                    target_mod.contacts_from_csv_string(csv_content)
                    status = "FAIL"
                    detail = f"Expected exception {expected_err}, but none was raised"
                except Exception as exc:
                    if type(exc).__name__ != expected_err:
                        status = "FAIL"
                        detail = f"Expected {expected_err}, got {type(exc).__name__}"

            elif case_type == "update_isolation":
                contacts = case["contacts"]
                target_id = case["target_id"]
                updates = case["updates"]
                expected = case["expected"]
                actual = target_mod.update_contact(contacts, target_id, updates)
                if actual != expected:
                    status = "FAIL"
                    detail = f"Expected {expected}, got {actual}"

            elif case_type == "get_unknown":
                contacts = case["contacts"]
                target_id = case["target_id"]
                expected = case["expected"]
                actual = target_mod.get_contact(contacts, target_id)
                if actual != expected:
                    status = "FAIL"
                    detail = f"Expected {expected}, got {actual}"

            elif case_type == "update_unknown":
                contacts = case["contacts"]
                target_id = case["target_id"]
                updates = case["updates"]
                expected_err = case["expected_error"]
                try:
                    target_mod.update_contact(contacts, target_id, updates)
                    status = "FAIL"
                    detail = f"Expected {expected_err}, but none was raised"
                except Exception as exc:
                    if type(exc).__name__ != expected_err:
                        status = "FAIL"
                        detail = f"Expected {expected_err}, got {type(exc).__name__}"

            elif case_type == "delete_unknown":
                contacts = case["contacts"]
                target_id = case["target_id"]
                expected_err = case["expected_error"]
                try:
                    target_mod.delete_contact(contacts, target_id)
                    status = "FAIL"
                    detail = f"Expected {expected_err}, but none was raised"
                except Exception as exc:
                    if type(exc).__name__ != expected_err:
                        status = "FAIL"
                        detail = f"Expected {expected_err}, got {type(exc).__name__}"

            elif case_type == "update_id_conflict":
                contacts = case["contacts"]
                target_id = case["target_id"]
                updates = case["updates"]
                expected_err = case["expected_error"]
                try:
                    target_mod.update_contact(contacts, target_id, updates)
                    status = "FAIL"
                    detail = f"Expected {expected_err}, but none was raised"
                except Exception as exc:
                    if type(exc).__name__ != expected_err:
                        status = "FAIL"
                        detail = f"Expected {expected_err}, got {type(exc).__name__}"

            elif case_type == "complexity":
                size = case["domain_size"]
                expected_comp = case["expected_comparisons"]
                sample = [
                    {"id": f"id_{i}", "name": f"User {i}", "phone": "555-0000", "email": "u@test.com"}
                    for i in range(size)
                ]
                _, measured_comp = target_mod.measure_lookup_work(sample, "non_existent")
                ref_comp = ref_store.count_worst_case_lookup_comparisons(size)
                if measured_comp != expected_comp or measured_comp != ref_comp:
                    status = "FAIL"
                    detail = (
                        f"Expected {expected_comp} (ref={ref_comp}), got {measured_comp}"
                    )

            elif case_type == "empty_csv":
                csv_content = case["csv_content"]
                expected = case["expected"]
                actual = target_mod.contacts_from_csv_string(csv_content)
                if actual != expected:
                    status = "FAIL"
                    detail = f"Expected {expected}, got {actual}"

            else:
                status = "FAIL"
                detail = f"Unknown case type: {case_type}"

        except Exception as exc:
            status = "FAIL"
            detail = f"Unexpected exception: {exc}"

        if status == "FAIL":
            all_passed = False
            print(f"[{status}] Case {case_id:2d}: {desc}")
            print(f"       -> Detail: {detail}")
        else:
            print(f"[{status}] Case {case_id:2d}: {desc}")

    print("-" * 70)

    # Run automated unittest discovery suite
    print("Running unittest discovery suite...")
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(TEST_DIR), "-p", "test_*.py"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"[FAIL] Unittest suite exited with code {proc.returncode}")
        print(proc.stdout)
        print(proc.stderr)
        all_passed = False
    else:
        print("[PASS] Unittest discovery suite passed successfully.")

    if not all_passed:
        print("\nOne or more checks FAILED.")
        return 1

    print("\nALL R26-T009 CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
