"""Native GTK4 Finance Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity


class FinanceActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Finance")
        self._rows = []
        self._build()

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(24); root.set_margin_bottom(24)
        root.set_margin_start(30); root.set_margin_end(30)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Finance tracker"])
        title = Gtk.Label(label="Finance", xalign=0); title.add_css_class("title-1"); root.append(title)
        self.amount = Gtk.Entry(); self.amount.set_placeholder_text("Amount"); self.amount.set_input_purpose(Gtk.InputPurpose.NUMBER)
        self.amount.update_property([Gtk.AccessibleProperty.LABEL], ["Amount"]); root.append(self.amount)
        self.description = Gtk.Entry(); self.description.set_placeholder_text("Description")
        self.description.update_property([Gtk.AccessibleProperty.LABEL], ["Description"]); root.append(self.description)
        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        income = Gtk.Button(label="Add income"); income.connect("clicked", lambda _b: self._add(1)); buttons.append(income)
        expense = Gtk.Button(label="Add expense"); expense.connect("clicked", lambda _b: self._add(-1)); buttons.append(expense)
        root.append(buttons)
        self.rows = Gtk.ListBox(); self.rows.set_vexpand(True); self.rows.update_property([Gtk.AccessibleProperty.LABEL], ["Transactions"]); root.append(self.rows)
        self.balance = Gtk.Label(label="Balance: 0.00", xalign=0); self.balance.add_css_class("heading"); root.append(self.balance)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } button { min-height: 42px; border-radius: 19px; } list { margin-top: 8px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _add(self, sign):
        try: value = abs(float(self.amount.get_text().strip())) * sign
        except ValueError: self.balance.set_text("Balance: enter a number"); return
        description = self.description.get_text().strip() or ("Income" if sign > 0 else "Expense")
        self._append_row(value, description)
        self.amount.set_text(""); self.description.set_text("")

    def _append_row(self, value, description):
        self._rows.append((value, description))
        row = Gtk.ListBoxRow(); row.set_child(Gtk.Label(label=f"{description}: {value:+.2f}", xalign=0)); self.rows.append(row)
        self.balance.set_text(f"Balance: {sum(v for v, _ in self._rows):.2f}")

    def read_file(self, file_path):
        """Restore transactions from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            transactions = payload.get("transactions", [])
            if not isinstance(transactions, list):
                raise ValueError("transactions must be a list")
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            transactions = []
        self._rows.clear()
        while (row := self.rows.get_row_at_index(0)) is not None:
            self.rows.remove(row)
        for transaction in transactions:
            if not isinstance(transaction, dict):
                continue
            try:
                value = float(transaction["value"])
                description = str(transaction.get("description", "Transaction")).strip() or "Transaction"
            except (KeyError, TypeError, ValueError):
                continue
            self._append_row(value, description)
        self.balance.set_text(f"Balance: {sum(v for v, _ in self._rows):.2f}")

    def write_file(self, file_path):
        """Save transactions as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"transactions": [{"value": value, "description": description} for value, description in self._rows]}, sort_keys=True) + "\n", encoding="utf-8")
