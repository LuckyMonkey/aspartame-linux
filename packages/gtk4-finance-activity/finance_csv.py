"""CSV interchange for Finance transactions (GTK3 ledger dictionaries)."""

from __future__ import annotations

import csv
import datetime
from pathlib import Path
from typing import Iterable


FIELDS = ("date", "description", "category", "amount", "type")


def write_csv(path: str | Path, transactions: Iterable[dict]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "date": datetime.date.fromordinal(t["date"]).isoformat(),
                "description": t["name"],
                "category": t["category"],
                "amount": f"{t['amount']:.2f}",
                "type": "income" if t["type"] == "credit" else "expense",
            })


def read_csv(path: str | Path, today: datetime.date | None = None) -> list[tuple]:
    """Rows of (description, kind, amount, category, date); bad rows raise."""
    today = today or datetime.date.today()
    with Path(path).open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {"description", "amount"}.issubset(reader.fieldnames):
            raise ValueError("CSV must contain description and amount columns")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                amount = abs(float(row["amount"]))
                date = datetime.date.fromisoformat(row["date"].strip()) if (row.get("date") or "").strip() else today
            except (TypeError, ValueError) as error:
                raise ValueError(f"invalid transaction on CSV line {line_number}") from error
            kind = (row.get("type") or "expense").strip().lower()
            if kind in {"income", "credit", "in"}:
                kind = "credit"
            elif kind in {"expense", "debit", "out", ""}:
                kind = "debit"
            else:
                raise ValueError(f"invalid transaction type on CSV line {line_number}")
            description = (row.get("description") or "").strip()
            rows.append((description, kind, amount, (row.get("category") or "").strip(), date))
        return rows
