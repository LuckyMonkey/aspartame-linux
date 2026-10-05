"""CSV interchange for the bounded GTK4 Finance transaction model."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


FIELDS = ("description", "amount", "type")


def write_csv(path: str | Path, rows: Iterable[tuple[float, str]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for value, description in rows:
            writer.writerow({
                "description": description,
                "amount": f"{abs(value):.2f}",
                "type": "income" if value >= 0 else "expense",
            })


def read_csv(path: str | Path) -> list[tuple[float, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {"description", "amount"}.issubset(reader.fieldnames):
            raise ValueError("CSV must contain description and amount columns")
        rows: list[tuple[float, str]] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                amount = abs(float(row["amount"]))
                description = (row.get("description") or "Transaction").strip() or "Transaction"
            except (TypeError, ValueError) as error:
                raise ValueError(f"invalid transaction on CSV line {line_number}") from error
            kind = (row.get("type") or "expense").strip().lower()
            if kind in {"income", "credit", "in"}:
                amount = abs(amount)
            elif kind in {"expense", "debit", "out", ""}:
                amount = -abs(amount)
            else:
                raise ValueError(f"invalid transaction type on CSV line {line_number}")
            rows.append((amount, description))
        return rows
