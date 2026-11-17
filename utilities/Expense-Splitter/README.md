# 💸 Expense Splitter

A beginner-friendly CLI utility for tracking shared costs, calculating each person's balance, and showing the minimum transfers needed to settle the bill.

---

## ✨ Features

- Track expenses with a payer and a list of participants
- Compute each person's net balance
- Show the smallest set of transfers needed to settle everyone up
- Supports a CLI and importable helpers for custom scripts
- Uses deterministic injected dependencies for clock, randomness, and file output in tests

---

## 🚦 Supported limits

The utility is designed for straightforward group expenses and follows these rules:

- `split_amount(total_amount, people)` requires `people > 0` and `total_amount >= 0`
- `amount` values must be non-negative
- each expense must include at least one participant
- values are rounded to 2 decimal places for money calculations
- the settlement logic prints the minimal transfers needed for the current balance sheet

---

## ▶️ Run command

From the repository root:

```bash
python3 utilities/Expense-Splitter/main.py --expense "Alice:90:Bob,Carol" --expense "Bob:50:Alice,Carol"
```

---

## 🧪 Exact input/output example

Input:

```bash
python3 utilities/Expense-Splitter/main.py --expense "Alice:90:Bob,Carol" --expense "Bob:50:Alice,Carol"
```

Output:

```text
💸 Expense Splitter Summary
============================
- Alice: should receive $65.00
- Bob: should receive $5.00
- Carol: owes $70.00

💳 Settlements
----------------------------
- Carol pays $65.00 to Alice
- Carol pays $5.00 to Bob

Generated at: 2026-11-17T16:57:10.680748+00:00
```

---

## 🧩 Supported input formats

The CLI accepts records in either of these formats:

```bash
payer:amount:participant1,participant2
```

or

```bash
payer amount participant1 participant2
```

Examples:

```bash
python3 utilities/Expense-Splitter/main.py --expense "Alice:120:Bob,Carol"
python3 utilities/Expense-Splitter/main.py --expense "Alice 120 Bob Carol"
```

---

## 🧠 Importable functions

The project is designed to be importable from Python scripts:

```python
from importlib.util import spec_from_file_location, module_from_spec

spec = spec_from_file_location("expense_splitter", "utilities/Expense-Splitter/main.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)

balances = module.calculate_balances([
    {"payer": "Alice", "amount": 120, "participants": ["Alice", "Bob", "Carol"]}
])
print(balances)
```

---

## 📁 Project layout

```text
utilities/Expense-Splitter/
├── README.md
├── test_main.py
└── main.py
```

---

## ✅ Repository registration

This project is registered through the repository's documented registry flow by updating `projects_registry.json` and validating it with:

```bash
python3 utils/registry_validator.py --strict
```
