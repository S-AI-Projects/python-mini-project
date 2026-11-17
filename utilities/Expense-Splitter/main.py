"""Expense Splitter utility.

This module exposes importable helpers for splitting shared costs and
calculating who owes whom. The CLI can be used interactively or with command-line
arguments.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence, Mapping, Protocol


class Clock(Protocol):
    """Minimal clock abstraction for deterministic tests."""

    def now(self) -> datetime:
        ...


class RandomSource(Protocol):
    """Minimal randomness interface for deterministic tests."""

    def choice(self, sequence: Sequence[str]) -> str:
        ...


class FileWriter(Protocol):
    """Minimal file-writing contract for deterministic tests."""

    def write_text(self, path: str | Path, contents: str) -> None:
        ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


def default_file_writer(path: str | Path, contents: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(contents, encoding="utf-8")


def split_amount(total_amount: float, people: int) -> float:
    """Split a total amount evenly across a number of people."""
    if people <= 0:
        raise ValueError("people must be greater than zero")
    if total_amount < 0:
        raise ValueError("total_amount must be non-negative")
    return round(float(total_amount) / float(people), 2)


def _normalize_people(participants: Iterable[str] | str | None) -> list[str]:
    if participants is None:
        return []
    if isinstance(participants, str):
        items = [participants]
    else:
        items = list(participants)
    cleaned: list[str] = []
    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            cleaned.append(text)
    return cleaned


def _normalize_record(record: Mapping[str, object] | Sequence[object]) -> dict[str, object]:
    if isinstance(record, Mapping):
        payer = record.get("payer")
        amount = record.get("amount")
        participants = record.get("participants", [payer]) if "participants" in record else [payer]
        return {
            "payer": str(payer),
            "amount": float(amount),
            "participants": _normalize_people(participants),
        }

    if isinstance(record, (list, tuple)) and len(record) >= 3:
        payer, amount, participants = record[0], record[1], record[2]
        return {
            "payer": str(payer),
            "amount": float(amount),
            "participants": _normalize_people(participants),
        }

    raise TypeError("Expense records must be mappings or (payer, amount, participants)")


def add_expense(
    expenses: list[Mapping[str, object] | Sequence[object]] | None,
    payer: str,
    amount: float,
    participants: Iterable[str] | str | None,
) -> list[dict[str, object]]:
    """Add an expense to an in-memory expense list and return the updated list."""
    if amount < 0:
        raise ValueError("amount must be non-negative")
    records = list(expenses) if expenses is not None else []
    payer_name = str(payer).strip()
    if not payer_name:
        raise ValueError("payer cannot be empty")
    normalized_people = _normalize_people(participants)
    if not normalized_people:
        normalized_people = [payer_name]
    if payer_name not in normalized_people:
        normalized_people = [*normalized_people, payer_name]
    records.append({"payer": payer_name, "amount": float(amount), "participants": normalized_people})
    return records


def calculate_balances(expenses: Iterable[Mapping[str, object] | Sequence[object]]) -> dict[str, float]:
    """Return each person's net balance.

    Positive balances mean the person should receive money; negative values mean
    they owe money.
    """
    balances: dict[str, float] = {}
    for record in expenses:
        normalized = _normalize_record(record)
        payer = normalized["payer"]
        amount = float(normalized["amount"])
        participants = normalized["participants"]

        if not participants:
            participants = [payer]

        share = round(amount / len(participants), 2)
        for person in participants:
            balances[person] = balances.get(person, 0.0) - share
        balances[payer] = balances.get(payer, 0.0) + amount

    return {name: round(value, 2) for name, value in balances.items()}


def settle_debts(expenses: Iterable[Mapping[str, object] | Sequence[object]]) -> list[dict[str, object]]:
    """Compute minimal transfers needed to settle all balances."""
    balances = calculate_balances(expenses)
    debtors: dict[str, float] = {name: -value for name, value in balances.items() if value < 0}
    creditors: dict[str, float] = {name: value for name, value in balances.items() if value > 0}
    transfers: list[dict[str, object]] = []

    while debtors and creditors:
        debtor_name = min(debtors, key=debtors.get)
        creditor_name = max(creditors, key=creditors.get)
        debtor_amount = debtors[debtor_name]
        creditor_amount = creditors[creditor_name]
        transfer = round(min(abs(debtor_amount), creditor_amount), 2)

        if transfer <= 0:
            break

        transfers.append({"from": debtor_name, "to": creditor_name, "amount": transfer})

        updated_debtor = round(debtor_amount + transfer, 2)
        updated_creditor = round(creditor_amount - transfer, 2)

        if abs(updated_debtor) < 0.005:
            del debtors[debtor_name]
        else:
            debtors[debtor_name] = updated_debtor

        if updated_creditor < 0.005:
            del creditors[creditor_name]
        else:
            creditors[creditor_name] = updated_creditor

    return transfers


def format_report(
    expenses: Iterable[Mapping[str, object] | Sequence[object]],
    *,
    clock: Clock | None = None,
) -> str:
    """Return a human-readable report of balances and settlements."""
    balances = calculate_balances(expenses)
    settlement = settle_debts(expenses)

    lines = ["💸 Expense Splitter Summary", "=" * 28]
    if not balances:
        lines.append("No expenses recorded.")
        return "\n".join(lines)

    for name in sorted(balances):
        amount = balances[name]
        if amount == 0:
            lines.append(f"- {name}: settled")
        elif amount > 0:
            lines.append(f"- {name}: should receive ${amount:.2f}")
        else:
            lines.append(f"- {name}: owes ${abs(amount):.2f}")

    lines.append("")
    lines.append("💳 Settlements")
    lines.append("-" * 28)
    if not settlement:
        lines.append("Everyone is settled up.")
    else:
        for item in settlement:
            lines.append(f"- {item['from']} pays ${item['amount']:.2f} to {item['to']}")

    current_clock = clock or SystemClock()
    timestamp = current_clock.now().isoformat()
    lines.append("")
    lines.append(f"Generated at: {timestamp}")

    return "\n".join(lines)


def choose_random_payer(
    participants: Sequence[str],
    *,
    rng: RandomSource | None = None,
) -> str:
    """Pick a payer from a set of participants using an injected RNG."""
    if not participants:
        raise ValueError("participants cannot be empty")
    source = rng if rng is not None else random.Random()
    return str(source.choice(list(participants)))


def save_report(
    report: str,
    destination: str | Path,
    *,
    file_writer: Callable[[str | Path, str], None] | None = None,
) -> str:
    """Persist a report using an injected file writer or the default filesystem writer."""
    writer = file_writer or default_file_writer
    writer(destination, report)
    return str(destination)


def split_bill(total_amount: float, people: int) -> dict[str, float]:
    """Convenience function for even splits across a group."""
    share = split_amount(total_amount, people)
    return {f"Person {index + 1}": share for index in range(people)}


def parse_expense_entry(entry: str) -> dict[str, object]:
    """Parse strings such as 'Alice:50:Bob,Carol' or 'Alice 50 Bob Carol'."""
    text = entry.strip()
    if not text:
        raise ValueError("expense entry cannot be empty")

    if ":" in text:
        parts = [part.strip() for part in text.split(":")]
        if len(parts) != 3:
            raise ValueError("expected format: payer:amount:participant1,participant2")
        payer, amount_text, people_text = parts
        participants = [person.strip() for person in people_text.split(",") if person.strip()]
        return {"payer": payer, "amount": float(amount_text), "participants": participants}

    parts = text.split()
    if len(parts) < 3:
        raise ValueError("expected format: payer amount participant1 participant2 ...")
    payer = parts[0]
    try:
        amount = float(parts[1])
    except ValueError as exc:
        raise ValueError("amount must be numeric") from exc
    participants = parts[2:]
    return {"payer": payer, "amount": amount, "participants": participants}


def _interactive_mode() -> dict[str, object]:
    print("💸 Expense Splitter")
    print("Enter each participant name separated by commas.")
    people_input = input("Participants: ").strip()
    if not people_input:
        raise ValueError("At least one participant is required.")
    people = [person.strip() for person in people_input.split(",") if person.strip()]

    records: list[dict[str, object]] = []
    print("Enter expenses as: payer:amount:person1,person2")
    print("Press Enter on a blank line to finish.")

    while True:
        raw = input("Expense: ").strip()
        if not raw:
            break
        record = parse_expense_entry(raw)
        record["participants"] = _normalize_people(record["participants"])
        if not record["participants"]:
            raise ValueError("Each expense must include at least one participant.")
        records.append(record)

    return {"participants": people, "expenses": records}


def _compute_cli_summary(expenses: Iterable[Mapping[str, object] | Sequence[object]]) -> dict[str, object]:
    balances = calculate_balances(expenses)
    settlements = settle_debts(expenses)
    return {"balances": balances, "settlements": settlements, "summary": format_report(expenses)}


def main(argv: Sequence[str] | None = None) -> dict[str, object]:
    """Command-line interface for the Expense Splitter."""
    parser = argparse.ArgumentParser(description="Split group bills and calculate who owes whom.")
    parser.add_argument(
        "--expense",
        action="append",
        default=[],
        help="Add an expense in the form payer:amount:person1,person2",
    )
    parser.add_argument(
        "--participant",
        dest="participants",
        action="append",
        default=[],
        help="Participant name. Can be repeated.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON instead of a readable summary.",
    )
    args = parser.parse_args(argv)

    records: list[dict[str, object]] = []
    for entry in args.expense:
        records.append(parse_expense_entry(entry))

    if records:
        result = _compute_cli_summary(records)
    else:
        try:
            interactive = _interactive_mode()
        except EOFError:
            parser.exit(0, "No input provided. Exiting.\n")
        if interactive.get("expenses"):
            result = _compute_cli_summary(interactive["expenses"])
        else:
            result = {"balances": {}, "settlements": [], "summary": format_report([])}

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["summary"])

    return result


if __name__ == "__main__":
    main()
