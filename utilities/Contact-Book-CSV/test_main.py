"""
Unit tests for Contact Book CSV.

Covers:
- Stable ID management and duplicate ID rejection
- Full CSV round-trip fidelity for names like "Ada, Jr."
- Row update isolation (updating id1 changes only that row)
- Explicit not-found result (None) for unknown ID queries
- KeyError on updating/deleting non-existent IDs
- Enforcement of stable IDs (ValueError on attempted ID change)
- Complexity experiment verifying bounded work at sizes 10, 100, 1000
- Silent import test (subprocess check verifying zero stdout/stderr)
- CLI tests with tempfile isolation, testing non-zero exit on missing file,
  unknown ID, duplicate ID, and bad arguments.
"""

from __future__ import annotations

import importlib.util
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parent / "main.py"
spec = importlib.util.spec_from_file_location("contact_book_csv_main", MODULE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Cannot load module from {MODULE_PATH}")
main_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_mod)

FIELDNAMES = main_mod.FIELDNAMES
load_contacts = main_mod.load_contacts
save_contacts = main_mod.save_contacts
add_contact = main_mod.add_contact
get_contact = main_mod.get_contact
update_contact = main_mod.update_contact
delete_contact = main_mod.delete_contact
measure_lookup_work = main_mod.measure_lookup_work
run_complexity_experiment = main_mod.run_complexity_experiment
contacts_to_csv_string = main_mod.contacts_to_csv_string
contacts_from_csv_string = main_mod.contacts_from_csv_string
cli_main = main_mod.main


class TestContactBookCSV(unittest.TestCase):
    """Test suite covering contract, invariants, boundaries, complexity, and CLI."""

    def test_roundtrip_ada_jr(self):
        """Name 'Ada, Jr.' round-trips cleanly through CSV DictWriter/DictReader."""
        original = [
            {
                "id": "id1",
                "name": "Ada, Jr.",
                "phone": "555-0100",
                "email": "ada@example.com",
            }
        ]
        csv_str = contacts_to_csv_string(original)
        loaded = contacts_from_csv_string(csv_str)
        self.assertEqual(loaded, original)
        self.assertEqual(loaded[0]["name"], "Ada, Jr.")

    def test_roundtrip_multiple_and_special_characters(self):
        """Multiple contacts with commas, quotes, and symbols round-trip correctly."""
        contacts = [
            {"id": "c1", "name": "Smith, John", "phone": "555-1001", "email": "john@example.com"},
            {"id": "c2", "name": 'Dr. "Bob" O\'Neil', "phone": "555-1002", "email": "bob@example.com"},
            {"id": "c3", "name": "René, Jr.", "phone": "555-1003", "email": "rene@example.com"},
        ]
        csv_str = contacts_to_csv_string(contacts)
        loaded = contacts_from_csv_string(csv_str)
        self.assertEqual(loaded, contacts)

    def test_reject_duplicate_id_on_add(self):
        """add_contact rejects existing ID with ValueError."""
        contacts = [
            {"id": "id1", "name": "Existing", "phone": "555-0001", "email": "e@example.com"}
        ]
        duplicate = {
            "id": "id1",
            "name": "Intruder",
            "phone": "555-9999",
            "email": "dup@example.com",
        }
        with self.assertRaises(ValueError) as ctx:
            add_contact(contacts, duplicate)
        self.assertIn("Duplicate contact ID: id1", str(ctx.exception))

    def test_reject_duplicate_id_on_csv_load(self):
        """load_contacts rejects CSV stream containing duplicate IDs with ValueError."""
        duplicate_csv = (
            "id,name,phone,email\n"
            "id1,First,555-0001,f@example.com\n"
            "id1,Second,555-0002,s@example.com\n"
        )
        with self.assertRaises(ValueError) as ctx:
            contacts_from_csv_string(duplicate_csv)
        self.assertIn("Duplicate contact ID: id1", str(ctx.exception))

    def test_add_contact_missing_fields_rejected(self):
        """add_contact requires id, name, phone, email keys."""
        with self.assertRaises(ValueError):
            add_contact([], {"id": "id1", "name": "Only Name"})

    def test_update_id1_changes_only_that_row(self):
        """Updating id1 changes only that row; other rows remain identical."""
        contacts = [
            {"id": "id1", "name": "Old One", "phone": "555-0001", "email": "one@example.com"},
            {"id": "id2", "name": "Two", "phone": "555-0002", "email": "two@example.com"},
            {"id": "id3", "name": "Three", "phone": "555-0003", "email": "three@example.com"},
        ]
        updates = {"name": "New One", "phone": "555-9999"}
        result = update_contact(contacts, "id1", updates)

        expected = [
            {"id": "id1", "name": "New One", "phone": "555-9999", "email": "one@example.com"},
            {"id": "id2", "name": "Two", "phone": "555-0002", "email": "two@example.com"},
            {"id": "id3", "name": "Three", "phone": "555-0003", "email": "three@example.com"},
        ]
        self.assertEqual(result, expected)
        # Verify original row 2 and 3 did not mutate
        self.assertEqual(result[1], contacts[1])
        self.assertEqual(result[2], contacts[2])

    def test_unknown_id_lookup_is_none(self):
        """Querying an unknown ID returns explicit None (not-found result)."""
        contacts = [
            {"id": "id1", "name": "Ada", "phone": "555-0100", "email": "ada@example.com"}
        ]
        self.assertIsNone(get_contact(contacts, "unknown_id_999"))

    def test_unknown_id_update_raises_key_error(self):
        """Updating an unknown ID raises KeyError."""
        contacts = [
            {"id": "id1", "name": "Ada", "phone": "555-0100", "email": "ada@example.com"}
        ]
        with self.assertRaises(KeyError) as ctx:
            update_contact(contacts, "unknown_id_999", {"name": "New"})
        self.assertIn("unknown_id_999", str(ctx.exception))

    def test_unknown_id_delete_raises_key_error(self):
        """Deleting an unknown ID raises KeyError."""
        contacts = [
            {"id": "id1", "name": "Ada", "phone": "555-0100", "email": "ada@example.com"}
        ]
        with self.assertRaises(KeyError) as ctx:
            delete_contact(contacts, "unknown_id_999")
        self.assertIn("unknown_id_999", str(ctx.exception))

    def test_stable_id_preservation_in_updates(self):
        """Attempting to modify the ID in update_contact raises ValueError."""
        contacts = [
            {"id": "id1", "name": "Ada", "phone": "555-0100", "email": "ada@example.com"}
        ]
        with self.assertRaises(ValueError) as ctx:
            update_contact(contacts, "id1", {"id": "id2", "name": "Changed"})
        self.assertIn("Cannot modify stable contact ID", str(ctx.exception))

        # Supplying identical ID is accepted as a no-op ID update
        ok = update_contact(contacts, "id1", {"id": "id1", "name": "Updated Ada"})
        self.assertEqual(ok[0]["name"], "Updated Ada")
        self.assertEqual(ok[0]["id"], "id1")

    def test_delete_contact_success(self):
        """delete_contact removes target contact and preserves others."""
        contacts = [
            {"id": "id1", "name": "One", "phone": "555-0001", "email": "one@example.com"},
            {"id": "id2", "name": "Two", "phone": "555-0002", "email": "two@example.com"},
        ]
        rem = delete_contact(contacts, "id1")
        self.assertEqual(len(rem), 1)
        self.assertEqual(rem[0]["id"], "id2")

    def test_empty_contact_book_boundary(self):
        """Empty contact book returns empty list."""
        empty_csv = "id,name,phone,email\n"
        loaded = contacts_from_csv_string(empty_csv)
        self.assertEqual(loaded, [])

        # In-memory save of empty list produces header
        buf = StringIO()
        save_contacts([], buf)
        self.assertEqual(buf.getvalue(), "id,name,phone,email\r\n")

    def test_complexity_bounded_work_at_three_sizes(self):
        """
        Verify bounded work at three domain sizes N in (10, 100, 1000).

        For linear scan lookup:
        - Worst-case comparisons seeking missing item = N.
        - Work is strictly bounded by W(N) <= N.
        """
        experiment_results = run_complexity_experiment((10, 100, 1000))
        self.assertEqual(set(experiment_results.keys()), {10, 100, 1000})

        self.assertEqual(experiment_results[10], 10)
        self.assertEqual(experiment_results[100], 100)
        self.assertEqual(experiment_results[1000], 1000)

        for n, comparisons in experiment_results.items():
            self.assertLessEqual(comparisons, n)
            self.assertEqual(comparisons, n)

    def test_silent_import(self):
        """Importing main.py produces zero stdout and zero stderr."""
        code = (
            "import importlib.util\n"
            f"spec = importlib.util.spec_from_file_location('cb_main', r'{MODULE_PATH}')\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(proc.stderr, "")

    def test_cli_subprocess_missing_file_exits_nonzero(self):
        """CLI with non-existent file on list/get/update exits non-zero."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "does_not_exist.csv"
            proc = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--file", str(missing_path), "--list"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Error loading file", proc.stderr)

    def test_cli_subprocess_bad_arguments_exits_nonzero(self):
        """CLI with invalid arguments exits non-zero."""
        proc = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--invalid-arg"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)

    def test_cli_subprocess_duplicate_id_exits_nonzero(self):
        """CLI --add with duplicate ID exits non-zero."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "contacts.csv"
            # Add initial contact
            proc1 = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--add",
                    "id1",
                    "Ada Lovelace",
                    "555-0100",
                    "ada@example.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc1.returncode, 0)

            # Attempt to add duplicate ID
            proc2 = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--add",
                    "id1",
                    "Duplicate Ada",
                    "555-9999",
                    "dup@example.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc2.returncode, 0)
            self.assertIn("Duplicate contact ID: id1", proc2.stderr)

    def test_cli_subprocess_unknown_id_exits_nonzero(self):
        """CLI --get with unknown ID exits non-zero."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "contacts.csv"
            # Initialize empty file
            save_contacts([], csv_path)

            proc = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--get",
                    "unknown_999",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Error: Contact ID 'unknown_999' not found", proc.stderr)

    def test_cli_subprocess_lifecycle_success(self):
        """CLI full lifecycle: add, get, update, list, delete, benchmark."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "contacts.csv"

            # 1. Add "Ada, Jr."
            proc_add = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--add",
                    "id1",
                    "Ada, Jr.",
                    "555-0100",
                    "ada@example.com",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_add.returncode, 0)

            # 2. Get id1
            proc_get = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--get",
                    "id1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_get.returncode, 0)
            self.assertIn("Ada, Jr.", proc_get.stdout)

            # 3. Update id1
            proc_upd = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--update",
                    "id1",
                    "--name",
                    "Ada Lovelace",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_upd.returncode, 0)

            # 4. List contacts
            proc_list = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--list",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_list.returncode, 0)
            self.assertIn("Ada Lovelace", proc_list.stdout)

            # 5. Delete id1
            proc_del = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--delete",
                    "id1",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_del.returncode, 0)

            # 6. Benchmark
            proc_bench = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--file",
                    str(csv_path),
                    "--benchmark",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_bench.returncode, 0)
            self.assertIn("Complexity Experiment", proc_bench.stdout)


if __name__ == "__main__":
    unittest.main()
