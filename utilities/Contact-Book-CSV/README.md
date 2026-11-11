# Contact Book CSV

A Python standard library utility for managing contacts with stable identifiers using `csv.DictReader` and `csv.DictWriter`.

## Overview

Contact Book CSV provides a clean interface and CLI for managing contacts stored in standard RFC 4180 CSV files. It ensures identity persistence, row update isolation, and full serialization fidelity for names with punctuation and commas (such as `"Ada, Jr."`).

### Key Features and Invariants
- **Stable IDs**: Every contact possesses a unique, immutable string identifier (`id`).
- **Duplicate Rejection**: Duplicate IDs are rejected during addition and CSV file loading by raising a `ValueError`.
- **Field Completeness**: Contacts consist of exactly four required attributes: `id`, `name`, `phone`, and `email`.
- **Row Update Isolation**: Updating a contact modifies only that specific row; all other rows remain untouched.
- **Explicit Not-Found Result**: Querying a missing ID produces an explicit `None` result. Updating or deleting an unknown ID raises a `KeyError`.
- **ID Immutability on Update**: In `update_contact`, if an `"id"` key is supplied in the updates dictionary, it must match the existing `contact_id`. Attempting to alter a contact's ID raises a `ValueError("Cannot modify stable contact ID...")`. This rule enforces stable identity semantics, preventing accidental key reassignment or identifier drift.
- **CSV Encoding and Formatting**: All files are opened using `encoding="utf-8"` and `newline=""` in accordance with standard library `csv` recommendations.

---

## CSV File Structure

The contact book CSV file uses the standard header:

```csv
id,name,phone,email
id1,"Ada, Jr.",555-0100,ada@example.com
id2,Grace Hopper,555-0101,grace@example.com
```

---

## CLI Usage

The CLI requires `--file PATH` for data operations, ensuring no fixed paths are assumed.

```bash
# Add a contact
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --add id1 "Ada, Jr." 555-0100 ada@example.com

# Get contact details by ID
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --get id1

# Update a contact
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --update id1 --name "Ada Lovelace"

# List all contacts
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --list

# Delete a contact
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --delete id1

# Run complexity experiment benchmark
python3 utilities/Contact-Book-CSV/main.py --file contacts.csv --benchmark
```

### Exit Codes
- `0`: Successful operation.
- `1`: Operational error (missing file, unknown ID, duplicate ID).
- `2`: Invalid command-line arguments.

---

## Examples

### 1. Round-Trip with Commas and Quotes ("Ada, Jr.")
```python
from utilities.Contact_Book_CSV.main import contacts_to_csv_string, contacts_from_csv_string

original = [{"id": "id1", "name": "Ada, Jr.", "phone": "555-0100", "email": "ada@example.com"}]
csv_text = contacts_to_csv_string(original)
# Produces: 'id,name,phone,email\r\nid1,"Ada, Jr.",555-0100,ada@example.com\r\n'
loaded = contacts_from_csv_string(csv_text)
assert loaded == original
```

### 2. Duplicate ID Rejection
```python
from utilities.Contact_Book_CSV.main import add_contact

contacts = [{"id": "id1", "name": "User 1", "phone": "555-0001", "email": "u1@test.com"}]
# Raises ValueError: Duplicate contact ID: id1
add_contact(contacts, {"id": "id1", "name": "User 2", "phone": "555-0002", "email": "u2@test.com"})
```

### 3. Update Isolation
```python
from utilities.Contact_Book_CSV.main import update_contact

contacts = [
    {"id": "id1", "name": "Old One", "phone": "555-0001", "email": "u1@test.com"},
    {"id": "id2", "name": "Two", "phone": "555-0002", "email": "u2@test.com"},
]
updated = update_contact(contacts, "id1", {"name": "New One"})
assert updated[0]["name"] == "New One"
assert updated[1] == contacts[1]  # row id2 is untouched
```

---

## Complexity Experiment

The focus of this mini-project is an empirical complexity experiment measuring bounded linear lookup work across three domain sizes:

| Domain Size ($N$) | Target Queried | Comparisons Measured | Bounded Work | Asymptotic Class |
|---|---|---|---|---|
| $N = 10$ | Non-existent ID | 10 | $W(10) \le 10$ | $\mathcal{O}(N)$ |
| $N = 100$ | Non-existent ID | 100 | $W(100) \le 100$ | $\mathcal{O}(N)$ |
| $N = 1000$ | Non-existent ID | 1000 | $W(1000) \le 1000$ | $\mathcal{O}(N)$ |

### Operation Count Analysis
In a sequential contact collection of size $N$, finding an element requires examining row identifiers one by one:
- **Best-case work**: 1 comparison (element is at index 0).
- **Average-case work**: $(N + 1) / 2$ comparisons.
- **Worst-case work**: $N$ comparisons (element is at the final index or not present in the dataset).

The linear upper bound $W(N) \le N$ holds across all input sizes, demonstrating predictable $\mathcal{O}(N)$ worst-case scaling.

---

## Supported Limits
- **File Encoding**: UTF-8.
- **Recommended Dataset Size**: Up to 100,000 records for in-memory list representation.
- **Identifier Format**: Non-empty UTF-8 string.

---

## Running Automated Tests

Run the test suite via standard unittest discovery:

```bash
python3 -m unittest discover -s utilities/Contact-Book-CSV -p "test_*.py" -v
```
