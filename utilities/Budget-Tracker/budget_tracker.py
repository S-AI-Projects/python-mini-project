"""
💰 Budget Tracker CLI Tool
A command-line budget tracker to manage income, expenses, and view summaries by category.
Data is saved persistently in a CSV file.
"""

import csv
import os
from datetime import datetime
from collections import defaultdict
from decimal import Decimal, InvalidOperation

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget_data.csv")

FIELDNAMES = ["id", "date", "type", "category", "description", "amount"]

# ─────────────────────────────────────────────
# FILE HELPERS
# ─────────────────────────────────────────────

def initialize_file(filepath=None):
    """Create the CSV file with headers if it doesn't exist.

    Supported boundary & contract:
    - Input: Optional str or Path-like filepath (defaults to DATA_FILE).
    - When file does not exist: Creates file and writes FIELDNAMES header line.
    - When file already exists: Idempotent no-op; leaves existing file unchanged.
    - Precondition anchors: FIELDNAMES = ["id", "date", "type", "category", "description", "amount"] (line 16), transactions = [] (line 28).
    """
    target = filepath if filepath is not None else DATA_FILE
    if not os.path.exists(target):
        with open(target, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def load_transactions():
    """Load all transactions from CSV and automatically migrating older files without IDs."""
    transactions = []

    with open(DATA_FILE, mode="r", newline="") as f:
        reader = csv.DictReader(f)

        has_id = "id" in (reader.fieldnames or [])

        for index, row in enumerate(reader, start=1):
            if has_id:
                row["id"] = int(row["id"])
            else:
                row["id"] = index
            row["amount"] = Decimal(row["amount"])
            transactions.append(row)

    if transactions and not has_id:
        save_transactions(transactions)

    return transactions

def save_transaction(entry):
    """Append a single transaction to the CSV."""
    with open(DATA_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        entry_copy = entry.copy()
        entry_copy["amount"] = str(entry_copy["amount"])
        writer.writerow(entry_copy)

def save_transactions(transactions):
    """Rewrite entire CSV with the current transactions."""
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for t in transactions:
            row = t.copy()
            row["amount"] = str(row["amount"])
            writer.writerow(row)

def get_next_id(transactions):
    """Get the next available ID."""
    if not transactions:
        return 1
    else:
        return max(t["id"] for t in transactions) + 1

def get_transaction_by_id(transactions, trans_id):
    """Retrieve transaction by ID."""
    for t in transactions:
        if t["id"] == trans_id:
            return t
    return None

# ─────────────────────────────────────────────
# CORE FEATURES
# ─────────────────────────────────────────────

def add_transaction(trans_type):
    """Add an income or expense entry."""
    print(f"\n── Add {trans_type.capitalize()} ──")

    category = input("Category (e.g. Food, Rent, Salary): ").strip()
    if not category:
        print("❌ Category cannot be empty.")
        return

    description = input("Description (optional): ").strip()

    try:
        amount_input = input("Amount (₹): ").strip()
        amount = Decimal(amount_input).quantize(Decimal("0.01"))
        if amount <= Decimal("0.00"):
            print("❌ Amount must be greater than 0.")
            return
    except (InvalidOperation, ValueError):
        print("❌ Invalid amount. Please enter a number.")
        return

    transactions = load_transactions()
    entry = {
        "id": get_next_id(transactions),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": trans_type,
        "category": category.capitalize(),
        "description": description,
        "amount": amount
    }
    save_transaction(entry)
    print(f"✅ {trans_type.capitalize()} of ₹{amount:.2f} added under '{category.capitalize()}'.")

def view_summary():
    """Show total income, expenses, and current balance."""
    transactions = load_transactions()

    if not transactions:
        print("\n📭 No transactions found.")
        return

    total_income = sum(
        (t["amount"] for t in transactions if t["type"] == "income"),
        Decimal("0.00")
    )

    total_expense = sum(
        (t["amount"] for t in transactions if t["type"] == "expense"),
        Decimal("0.00")
    )

    balance = total_income - total_expense

    print("\n" + "═" * 35)
    print("       💰 BUDGET SUMMARY")
    print("═" * 35)
    print(f"  Total Income  : ₹{total_income:>10.2f}")
    print(f"  Total Expenses: ₹{total_expense:>10.2f}")
    print("─" * 35)
    balance_label = "✅ Balance" if balance >= 0 else "⚠️  Deficit"
    print(f"  {balance_label}  : ₹{abs(balance):>10.2f}")
    print("═" * 35)

def view_category_summary():
    """Show spending/income broken down by category."""
    transactions = load_transactions()

    if not transactions:
        print("\n📭 No transactions found.")
        return

    income_by_cat = defaultdict(lambda: Decimal("0.00"))
    expense_by_cat = defaultdict(lambda: Decimal("0.00"))

    for t in transactions:
        if t["type"] == "income":
            income_by_cat[t["category"]] += t["amount"]
        else:
            expense_by_cat[t["category"]] += t["amount"]

    print("\n" + "═" * 35)
    print("   📊 CATEGORY-WISE BREAKDOWN")
    print("═" * 35)

    if income_by_cat:
        print("\n  📈 Income:")
        for cat, amt in sorted(income_by_cat.items()):
            print(f"    {cat:<20} ₹{amt:.2f}")

    if expense_by_cat:
        print("\n  📉 Expenses:")
        for cat, amt in sorted(expense_by_cat.items()):
            print(f"    {cat:<20} ₹{amt:.2f}")

    print("═" * 35)

def view_all_transactions():
    """Display all recorded transactions."""
    transactions = load_transactions()

    if not transactions:
        print("\n📭 No transactions found.")
        return

    print("\n" + "═" * 70)
    print(f"  {'ID':<4} {'DATE':<17} {'TYPE':<10} {'CATEGORY':<15} {'DESCRIPTION':<15} {'AMOUNT':>8}")
    print("─" * 70)

    for t in transactions:
        symbol = "+" if t["type"] == "income" else "-"
        print(
            f"  {t['id']:<4} {t['date']:<17} {t['type']:<10} {t['category']:<15} "
            f"{t['description'][:14]:<15} {symbol}₹{t['amount']:>7.2f}"
        )

    print("═" * 70)

def delete_all_transactions():
    """Clear all transaction data after confirmation."""
    confirm = input("\n⚠️  Are you sure you want to delete ALL data? (yes/no): ").strip().lower()
    if confirm == "yes":
        with open(DATA_FILE, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        print("🗑️  All transactions deleted.")
    else:
        print("❌ Cancelled.")

def edit_transaction():
    """Edit a transaction, updating in-place."""
    transactions = load_transactions()
    if not transactions:
        print("\n📭 No transactions to edit.")
        return

    print("\nSelect a transaction to edit by ID:")
    for t in transactions:
        print(f"  {t['id']}: {t['date']} | {t['type']} | {t['category']} | {t['description']} | ₹{t['amount']:.2f}")

    try:
        trans_id_input = input("Enter Transaction ID: ").strip()
        trans_id = int(trans_id_input)
    except ValueError:
        print("❌ Invalid ID.")
        return

    transaction = get_transaction_by_id(transactions, trans_id)
    if not transaction:
        print("❌ Transaction ID not found.")
        return

    new_type_input = input(f"Type [{transaction['type']}] (income/expense): ").strip().lower()
    if new_type_input:
        if new_type_input not in ("income", "expense"):
            print("❌ Invalid type.")
            return
        transaction["type"] = new_type_input

    new_category = input(f"Category [{transaction['category']}]: ").strip()
    if new_category:
        transaction['category'] = new_category.capitalize()

    new_description = input(f"Description [{transaction['description']}]: ").strip()
    if new_description:
        transaction['description'] = new_description

    new_amount_str = input(f"Amount (₹) [{transaction['amount']}]: ").strip()
    if new_amount_str:
        try:
            new_amount = Decimal(new_amount_str).quantize(Decimal("0.01"))
            if new_amount <= Decimal("0.00"):
                print("❌ Amount must be greater than 0.")
                return
            transaction['amount'] = new_amount
        except (InvalidOperation, ValueError):
            print("❌ Invalid amount.")
            return

    save_transactions(transactions)
    print("✅ Transaction updated successfully.")

def delete_transaction():
    """Delete a specific transaction by ID."""
    transactions = load_transactions()
    if not transactions:
        print("\n📭 No transactions to delete.")
        return

    print("\nSelect a transaction to delete by ID:")
    for t in transactions:
        print(f"  {t['id']}: {t['date']} | {t['type']} | {t['category']} | {t['description']} | ₹{t['amount']:.2f}")

    try:
        trans_id_input = input("Enter Transaction ID: ").strip()
        trans_id = int(trans_id_input)
    except ValueError:
        print("❌ Invalid ID.")
        return

    new_transactions = [t for t in transactions if t["id"] != trans_id]
    if len(new_transactions) == len(transactions):
        print("❌ Transaction ID not found.")
        return

    save_transactions(new_transactions)
    print("🗑️  Transaction deleted.")

# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

def print_menu():
    print("\n" + "═" * 35)
    print("      💰 BUDGET TRACKER CLI")
    print("═" * 35)
    print("  1. ➕ Add Income")
    print("  2. ➖ Add Expense")
    print("  3. 📋 View All Transactions")
    print("  4. 📊 View Summary")
    print("  5. 🗂️  Category-wise Breakdown")
    print("  6. ✏️ Edit a Transaction")
    print("  7. 🗑️ Delete a Transaction")
    print("  8. 🗑️ Clear All Data")
    print("  9. 🚪 Exit")
    print("═" * 35)

def main():
    initialize_file()
    print("\n👋 Welcome to Budget Tracker!")

    while True:
        print_menu()
        choice = input("  Enter your choice (1-9): ").strip()

        if choice == "1":
            add_transaction("income")
        elif choice == "2":
            add_transaction("expense")
        elif choice == "3":
            view_all_transactions()
        elif choice == "4":
            view_summary()
        elif choice == "5":
            view_category_summary()
        elif choice == "6":
            edit_transaction()
        elif choice == "7":
            delete_transaction()
        elif choice == "8":
            delete_all_transactions()
        elif choice == "9":
            print("\n👋 Goodbye! Keep tracking your budget. 💸\n")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()
