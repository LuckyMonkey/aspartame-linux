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
        root.set_hexpand(True); root.set_vexpand(True)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Finance tracker"])
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        body.set_hexpand(True)
        body.set_vexpand(True)
        body.set_halign(Gtk.Align.FILL)
        body.set_valign(Gtk.Align.FILL)
        root.append(body)
        title = Gtk.Label(label="Finance", xalign=0); title.add_css_class("title-1"); body.append(title)
        self.amount = Gtk.Entry(); self.amount.set_placeholder_text("Amount"); self.amount.set_input_purpose(Gtk.InputPurpose.NUMBER)
        self.amount.update_property([Gtk.AccessibleProperty.LABEL], ["Amount"])
        self.amount.set_size_request(220, -1)
        self.amount.set_hexpand(False)
        self.description = Gtk.Entry(); self.description.set_placeholder_text("Description")
        self.description.update_property([Gtk.AccessibleProperty.LABEL], ["Description"])
        self.description.set_hexpand(True)
        form = Gtk.Grid(column_spacing=12, row_spacing=6)
        form.set_hexpand(True)
        description_label = Gtk.Label(label="Description", xalign=0)
        amount_label = Gtk.Label(label="Amount", xalign=0)
        form.attach(description_label, 0, 0, 1, 1)
        form.attach(amount_label, 1, 0, 1, 1)
        form.attach(self.description, 0, 1, 1, 1)
        form.attach(self.amount, 1, 1, 1, 1)
        body.append(form)
        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        income = Gtk.Button(label="Add income"); income.connect("clicked", lambda _b: self._add(1)); buttons.append(income)
        expense = Gtk.Button(label="Add expense"); expense.connect("clicked", lambda _b: self._add(-1)); buttons.append(expense)
        body.append(buttons)
        header = Gtk.Grid(column_spacing=12)
        header.set_margin_top(8)
        header.set_hexpand(True)
        description_heading = Gtk.Label(label="Description", xalign=0)
        description_heading.set_hexpand(True)
        amount_heading = Gtk.Label(label="Amount", xalign=1)
        amount_heading.set_halign(Gtk.Align.END)
        header.attach(description_heading, 0, 0, 1, 1)
        header.attach(amount_heading, 1, 0, 1, 1)
        body.append(header)
        self.empty_state = Gtk.Label(label="No transactions yet. Add income or an expense to begin.", xalign=0, wrap=True)
        self.empty_state.add_css_class("dim-label")
        self.empty_state.update_property([Gtk.AccessibleProperty.LABEL], ["No transactions yet"])
        body.append(self.empty_state)
        self.rows = Gtk.ListBox(); self.rows.set_vexpand(True); self.rows.set_hexpand(True); self.rows.update_property([Gtk.AccessibleProperty.LABEL], ["Transactions"]); body.append(self.rows)
        self.balance = Gtk.Label(label="Balance: 0.00", xalign=0); self.balance.add_css_class("heading"); body.append(self.balance)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } button { min-height: 42px; border-radius: 19px; } list { margin-top: 8px; } listboxrow { padding: 10px 12px; }")
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
        row = Gtk.ListBoxRow()
        table_row = Gtk.Grid(column_spacing=12)
        table_row.set_hexpand(True)
        description_label = Gtk.Label(label=description, xalign=0)
        description_label.set_hexpand(True)
        amount_label = Gtk.Label(label=f"{value:+.2f}", xalign=1)
        amount_label.set_halign(Gtk.Align.END)
        table_row.attach(description_label, 0, 0, 1, 1)
        table_row.attach(amount_label, 1, 0, 1, 1)
        row.set_child(table_row)
        self.rows.append(row)
        self.empty_state.set_visible(False)
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
        self.empty_state.set_visible(not self._rows)
        self.balance.set_text(f"Balance: {sum(v for v, _ in self._rows):.2f}")

    def write_file(self, file_path):
        """Save transactions as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"transactions": [{"value": value, "description": description} for value, description in self._rows]}, sort_keys=True) + "\n", encoding="utf-8")
