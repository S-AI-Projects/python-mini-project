"""
Contact Book CSV

A lightweight contact book manager that reads and writes contacts with stable IDs
using csv.DictReader and csv.DictWriter.

Core Contracts:
- Contacts have stable IDs and four fields: id, name, phone, email.
- Duplicate IDs are rejected during addition and CSV loading with ValueError.
- Full CSV round-trip fidelity for complex names such as "Ada, Jr.".
- Updating an ID alters only that row and preserves all other rows intact.
- Querying an unknown ID produces an explicit not-found result (None).
- Updating or deleting an unknown ID raises KeyError.
- Updating an ID enforces stability: attempting to change the ID raises ValueError.
- Complexity experiment: measures bounded lookup work (comparison count) across
  three domain sizes (N = 10, 100, 1000).
"""

from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path
import sys
from typing import TextIO

FIELDNAMES: list[str] = ["id", "name", "phone", "email"]


def load_contacts(source: str | Path | TextIO) -> list[dict[str, str]]:
    """
    Load contacts from a CSV file path, Path object, or text stream.

    Validates that all required headers are present and verifies ID uniqueness.

    Args:
        source: File path (str or Path) or readable text stream (TextIO).

    Returns:
        List of contact dictionaries.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If duplicate IDs are encountered or required fields are missing.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(f"Contact file not found: {source}")
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            return _parse_csv_stream(f)
    else:
        return _parse_csv_stream(source)


def _parse_csv_stream(stream: TextIO) -> list[dict[str, str]]:
    """Helper to parse CSV stream using csv.DictReader."""
    reader = csv.DictReader(stream)
    if reader.fieldnames is None:
        return []

    missing = [f for f in FIELDNAMES if f not in reader.fieldnames]
    if missing:
        raise ValueError(f"CSV missing required field(s): {', '.join(missing)}")

    contacts: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for row_idx, row in enumerate(reader, start=1):
        cid = (row.get("id") or "").strip()
        if not cid:
            raise ValueError(f"Row {row_idx} is missing a valid 'id'")
        if cid in seen_ids:
            raise ValueError(f"Duplicate contact ID: {cid}")
        seen_ids.add(cid)

        contact = {field: (row.get(field) or "") for field in FIELDNAMES}
        contacts.append(contact)

    return contacts


def save_contacts(contacts: list[dict[str, str]], target: str | Path | TextIO) -> None:
    """
    Save contacts to a CSV file path, Path object, or text stream.

    Args:
        contacts: List of contact dictionaries.
        target: Target file path or writable text stream.
    """
    if isinstance(target, (str, Path)):
        path = Path(target)
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            _write_csv_stream(contacts, f)
    else:
        _write_csv_stream(contacts, target)


def _write_csv_stream(contacts: list[dict[str, str]], stream: TextIO) -> None:
    """Helper to write CSV stream using csv.DictWriter."""
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES)
    writer.writeheader()
    for contact in contacts:
        row = {field: contact.get(field, "") for field in FIELDNAMES}
        writer.writerow(row)


def add_contact(contacts: list[dict[str, str]], new_contact: dict[str, str]) -> list[dict[str, str]]:
    """
    Add a new contact to the contact list, rejecting duplicate IDs.

    Args:
        contacts: Current list of contacts.
        new_contact: New contact dictionary containing id, name, phone, email.

    Returns:
        A new list of contacts containing the added contact.

    Raises:
        ValueError: If required keys are missing or the ID already exists.
    """
    missing_keys = [k for k in FIELDNAMES if k not in new_contact]
    if missing_keys:
        raise ValueError(f"Contact missing required key(s): {', '.join(missing_keys)}")

    cid = str(new_contact["id"]).strip()
    if not cid:
        raise ValueError("Contact ID cannot be empty")

    if any(c["id"] == cid for c in contacts):
        raise ValueError(f"Duplicate contact ID: {cid}")

    cleaned = {field: str(new_contact[field]) for field in FIELDNAMES}
    return [*contacts, cleaned]


def get_contact(contacts: list[dict[str, str]], contact_id: str) -> dict[str, str] | None:
    """
    Find and return a contact by ID, returning None if not found.

    Args:
        contacts: Current list of contacts.
        contact_id: Target contact ID string.

    Returns:
        Copy of the matching contact dictionary, or None if not found.
    """
    for c in contacts:
        if c["id"] == contact_id:
            return dict(c)
    return None


def update_contact(
    contacts: list[dict[str, str]],
    contact_id: str,
    updates: dict[str, str],
) -> list[dict[str, str]]:
    """
    Update an existing contact by ID, modifying only that row.

    Stable-ID Rule:
    Contact IDs are stable identifiers. If 'id' is supplied in updates, it must
    match contact_id. Attempting to change an ID to a different value raises ValueError.

    Args:
        contacts: Current list of contacts.
        contact_id: Target contact ID string.
        updates: Dictionary of fields to update.

    Returns:
        A new list of contacts with only the specified row updated.

    Raises:
        KeyError: If contact_id does not exist.
        ValueError: If updates attempts to change the stable ID.
    """
    if "id" in updates and str(updates["id"]).strip() != contact_id:
        raise ValueError(
            f"Cannot modify stable contact ID from '{contact_id}' to '{updates['id']}'"
        )

    found = False
    updated_list: list[dict[str, str]] = []

    for c in contacts:
        if c["id"] == contact_id:
            found = True
            new_row = dict(c)
            for k in ("name", "phone", "email"):
                if k in updates:
                    new_row[k] = str(updates[k])
            updated_list.append(new_row)
        else:
            updated_list.append(dict(c))

    if not found:
        raise KeyError(f"Contact ID '{contact_id}' not found")

    return updated_list


def delete_contact(contacts: list[dict[str, str]], contact_id: str) -> list[dict[str, str]]:
    """
    Delete a contact by ID.

    Args:
        contacts: Current list of contacts.
        contact_id: Target contact ID string.

    Returns:
        A new list of contacts without the deleted contact.

    Raises:
        KeyError: If contact_id is not found.
    """
    if not any(c["id"] == contact_id for c in contacts):
        raise KeyError(f"Contact ID '{contact_id}' not found")

    return [dict(c) for c in contacts if c["id"] != contact_id]


def measure_lookup_work(contacts: list[dict[str, str]], target_id: str) -> tuple[dict[str, str] | None, int]:
    """
    Look up a contact while counting the number of comparison operations performed.

    Args:
        contacts: List of contacts.
        target_id: Target ID to find.

    Returns:
        Tuple of (matching contact or None, comparison count).
    """
    comparisons = 0
    for c in contacts:
        comparisons += 1
        if c["id"] == target_id:
            return (dict(c), comparisons)
    return (None, comparisons)


def run_complexity_experiment(sizes: tuple[int, int, int] = (10, 100, 1000)) -> dict[int, int]:
    """
    Measure worst-case lookup operations at three domain sizes.

    In a list of size N, worst-case linear search (seeking an element at the
    end or a non-existent element) performs exactly N row comparisons.

    Args:
        sizes: Tuple of domain sizes (default 10, 100, 1000).

    Returns:
        Dictionary mapping domain size N to measured comparison count.
    """
    results: dict[int, int] = {}
    for n in sizes:
        sample_contacts = [
            {"id": f"id_{i}", "name": f"User {i}", "phone": f"555-{i:04d}", "email": f"user{i}@test.com"}
            for i in range(n)
        ]
        # Worst-case: search for non-existent ID inspects all N items
        _, comparisons = measure_lookup_work(sample_contacts, "non_existent_id")
        results[n] = comparisons
    return results


def contacts_to_csv_string(contacts: list[dict[str, str]]) -> str:
    """Helper to convert contacts list to an in-memory CSV string."""
    buf = StringIO()
    save_contacts(contacts, buf)
    return buf.getvalue()


def contacts_from_csv_string(csv_text: str) -> list[dict[str, str]]:
    """Helper to load contacts from an in-memory CSV string."""
    buf = StringIO(csv_text)
    return load_contacts(buf)


def main(argv: list[str] | None = None) -> int:
    """
    CLI interface for Contact Book CSV.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, non-zero on failure.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Contact Book CSV - Manage contacts with stable IDs."
    )
    parser.add_argument("--file", required=True, help="Path to contacts CSV file.")

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--list", action="store_true", help="List all contacts.")
    action_group.add_argument("--get", metavar="ID", help="Get contact details by ID.")
    action_group.add_argument(
        "--add",
        nargs=4,
        metavar=("ID", "NAME", "PHONE", "EMAIL"),
        help="Add contact: ID NAME PHONE EMAIL.",
    )
    action_group.add_argument(
        "--update",
        metavar="ID",
        help="Update contact by ID (use with --name, --phone, and/or --email).",
    )
    action_group.add_argument("--delete", metavar="ID", help="Delete contact by ID.")
    action_group.add_argument(
        "--benchmark",
        action="store_true",
        help="Run complexity experiment measuring lookup work at sizes 10, 100, 1000.",
    )

    parser.add_argument("--name", help="Updated contact name (used with --update).")
    parser.add_argument("--phone", help="Updated contact phone (used with --update).")
    parser.add_argument("--email", help="Updated contact email (used with --update).")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    # Benchmark can run independently of file existence if requested, but --file is parsed
    if args.benchmark:
        exp = run_complexity_experiment()
        print("=== Complexity Experiment: Worst-case Lookup Operations ===")
        for size, count in exp.items():
            print(f"Domain size N={size:4d} -> Comparisons: {count:4d} (Bound: <= {size})")
        return 0

    csv_path = Path(args.file)

    if args.list:
        try:
            contacts = load_contacts(csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error loading file: {exc}\n")
            return 1
        if not contacts:
            print("Contact book is empty.")
            return 0
        for c in contacts:
            print(f"[{c['id']}] {c['name']} | {c['phone']} | {c['email']}")
        return 0

    if args.get:
        try:
            contacts = load_contacts(csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error loading file: {exc}\n")
            return 1
        contact = get_contact(contacts, args.get)
        if contact is None:
            sys.stderr.write(f"Error: Contact ID '{args.get}' not found.\n")
            return 1
        print(f"ID:    {contact['id']}")
        print(f"Name:  {contact['name']}")
        print(f"Phone: {contact['phone']}")
        print(f"Email: {contact['email']}")
        return 0

    if args.add:
        cid, name, phone, email = args.add
        contacts: list[dict[str, str]] = []
        if csv_path.exists():
            try:
                contacts = load_contacts(csv_path)
            except Exception as exc:
                sys.stderr.write(f"Error reading file: {exc}\n")
                return 1

        new_c = {"id": cid, "name": name, "phone": phone, "email": email}
        try:
            updated_contacts = add_contact(contacts, new_c)
            save_contacts(updated_contacts, csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error adding contact: {exc}\n")
            return 1
        print(f"Added contact [{cid}] successfully.")
        return 0

    if args.update:
        if not csv_path.exists():
            sys.stderr.write(f"Error: File '{csv_path}' does not exist.\n")
            return 1
        try:
            contacts = load_contacts(csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error reading file: {exc}\n")
            return 1

        updates: dict[str, str] = {}
        if args.name is not None:
            updates["name"] = args.name
        if args.phone is not None:
            updates["phone"] = args.phone
        if args.email is not None:
            updates["email"] = args.email

        try:
            updated_contacts = update_contact(contacts, args.update, updates)
            save_contacts(updated_contacts, csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error updating contact: {exc}\n")
            return 1
        print(f"Updated contact [{args.update}] successfully.")
        return 0

    if args.delete:
        if not csv_path.exists():
            sys.stderr.write(f"Error: File '{csv_path}' does not exist.\n")
            return 1
        try:
            contacts = load_contacts(csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error reading file: {exc}\n")
            return 1
        try:
            updated_contacts = delete_contact(contacts, args.delete)
            save_contacts(updated_contacts, csv_path)
        except Exception as exc:
            sys.stderr.write(f"Error deleting contact: {exc}\n")
            return 1
        print(f"Deleted contact [{args.delete}] successfully.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
