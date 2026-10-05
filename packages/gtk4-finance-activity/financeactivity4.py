"""Native GTK4 Finance Activity."""

import json
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity
from finance_csv import read_csv, write_csv


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
        self.amount.set_width_chars(10)
        self.amount.set_max_width_chars(16)
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
        form_frame = Gtk.Frame(label="New transaction")
        form_frame.add_css_class("finance-pane")
        form_frame.set_halign(Gtk.Align.FILL)
        form_frame.set_child(form)
        body.append(form_frame)
        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        buttons.set_halign(Gtk.Align.END)
        income = Gtk.Button(label="Add income"); income.connect("clicked", lambda _b: self._add(1)); buttons.append(income)
        expense = Gtk.Button(label="Add expense"); expense.connect("clicked", lambda _b: self._add(-1)); buttons.append(expense)
        import_button = Gtk.Button(label="Import CSV")
        import_button.set_tooltip_text("Replace transactions from a CSV file")
        import_button.update_property([Gtk.AccessibleProperty.LABEL], ["Import transactions from CSV"])
        import_button.connect("clicked", self._import_csv)
        buttons.append(import_button)
        export_button = Gtk.Button(label="Export CSV")
        export_button.set_tooltip_text("Save transactions as a CSV file")
        export_button.update_property([Gtk.AccessibleProperty.LABEL], ["Export transactions to CSV"])
        export_button.connect("clicked", self._export_csv)
        buttons.append(export_button)
        body.append(buttons)

        transaction_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        transaction_content.set_vexpand(True)
        header = Gtk.Grid(column_spacing=12)
        header.set_margin_top(8)
        description_heading = Gtk.Label(label="Description", xalign=0)
        description_heading.set_hexpand(True)
        amount_heading = Gtk.Label(label="Amount", xalign=1)
        amount_heading.set_halign(Gtk.Align.END)
        amount_heading.set_width_chars(10)
        actions_heading = Gtk.Label(label="Actions", xalign=0.5)
        actions_heading.set_width_chars(10)
        header.attach(description_heading, 0, 0, 1, 1)
        header.attach(amount_heading, 1, 0, 1, 1)
        header.attach(actions_heading, 2, 0, 1, 1)
        transaction_content.append(header)
        self.empty_state = Gtk.Label(label="No transactions yet. Add income or an expense to begin.", wrap=True)
        self.empty_state.add_css_class("dim-label")
        self.empty_state.set_halign(Gtk.Align.CENTER)
        self.empty_state.set_valign(Gtk.Align.CENTER)
        self.empty_state.set_vexpand(True)
        self.empty_state.set_justify(Gtk.Justification.CENTER)
        self.empty_state.set_max_width_chars(48)
        self.empty_state.add_css_class("empty-state")
        self.empty_state.update_property([Gtk.AccessibleProperty.LABEL], ["No transactions yet"])
        transaction_content.append(self.empty_state)
        self.rows = Gtk.ListBox(); self.rows.set_vexpand(True); self.rows.set_hexpand(True); self.rows.set_visible(False); self.rows.update_property([Gtk.AccessibleProperty.LABEL], ["Transactions"])
        transaction_content.append(self.rows)
        rows_frame = Gtk.Frame(label="Transactions")
        rows_frame.add_css_class("finance-pane")
        rows_frame.set_vexpand(True); rows_frame.set_hexpand(True)
        rows_frame.set_child(transaction_content)
        body.append(rows_frame)
        self.status = Gtk.Label(label="Ready", xalign=0); self.status.add_css_class("dim-label"); self.status.set_hexpand(True)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.append(self.status)
        self.balance = Gtk.Label(label="Balance: 0.00", xalign=1); self.balance.set_halign(Gtk.Align.END); self.balance.add_css_class("heading"); footer.append(self.balance)
        body.append(footer)
        self.set_canvas(root)
        provider = Gtk.CssProvider(); provider.load_from_data(b"entry { min-height: 42px; } button { min-height: 42px; border-radius: 19px; } frame.finance-pane { border: 1px solid #8aa8b8; border-radius: 10px; padding: 10px; } label.empty-state { background: #f1f5f7; border-radius: 12px; padding: 28px 24px; color: #52636b; } list { margin-top: 8px; } listboxrow { padding: 10px 12px; }")
        display = Gdk.Display.get_default()
        if display: Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _add(self, sign):
        try: value = abs(float(self.amount.get_text().strip())) * sign
        except ValueError: self.status.set_text("Unable to add: enter a number"); return
        description = self.description.get_text().strip() or ("Income" if sign > 0 else "Expense")
        self._append_row(value, description)
        self.amount.set_text(""); self.description.set_text("")
        self.status.set_text("Added: %s" % description)

    def _append_row(self, value, description):
        self._rows.append((value, description))
        self._refresh_rows()

    def _refresh_rows(self):
        while (row := self.rows.get_row_at_index(0)) is not None:
            self.rows.remove(row)
        for index, (value, description) in enumerate(self._rows):
            row = Gtk.ListBoxRow()
            table_row = Gtk.Grid(column_spacing=12)
            table_row.set_hexpand(True)
            description_label = Gtk.Label(label=description, xalign=0)
            description_label.set_hexpand(True)
            amount_label = Gtk.Label(label=f"{value:+.2f}", xalign=1)
            amount_label.set_halign(Gtk.Align.END)
            amount_label.set_width_chars(10)
            remove = Gtk.Button(label=f"Remove {description}")
            remove.set_tooltip_text(f"Remove transaction: {description}")
            remove.update_property([Gtk.AccessibleProperty.LABEL], [f"Remove transaction: {description}"])
            remove.connect("clicked", self._remove_row, index)
            table_row.attach(description_label, 0, 0, 1, 1)
            table_row.attach(amount_label, 1, 0, 1, 1)
            table_row.attach(remove, 2, 0, 1, 1)
            row.set_child(table_row)
            self.rows.append(row)
        self.empty_state.set_visible(not self._rows)
        self.rows.set_visible(bool(self._rows))
        self.balance.set_text(f"Balance: {sum(v for v, _ in self._rows):.2f}")

    def _remove_row(self, _button, index):
        if 0 <= index < len(self._rows):
            description = self._rows[index][1]
            self._rows.pop(index)
            self._refresh_rows()
            self.status.set_text("Removed: %s" % description)

    def _import_csv(self, _button):
        Gtk.FileDialog(title="Import Finance CSV").open(self, None, self._import_csv_chosen)

    def _import_csv_chosen(self, dialog, result):
        try:
            file_obj = dialog.open_finish(result)
            path = file_obj.get_path() if file_obj is not None else None
            if not path:
                return
            self._rows = read_csv(path)
        except Exception as error:
            self.status.set_text("Import failed: %s" % error)
            return
        self._refresh_rows()
        self.status.set_text("Imported %d transaction%s" % (len(self._rows), "" if len(self._rows) == 1 else "s"))

    def _export_csv(self, _button):
        Gtk.FileDialog(title="Export Finance CSV").save(self, None, self._export_csv_chosen)

    def _export_csv_chosen(self, dialog, result):
        try:
            file_obj = dialog.save_finish(result)
            path = file_obj.get_path() if file_obj is not None else None
            if not path:
                return
            write_csv(path, self._rows)
        except Exception as error:
            self.status.set_text("Export failed: %s" % error)
            return
        self.status.set_text("Exported %d transaction%s" % (len(self._rows), "" if len(self._rows) == 1 else "s"))

    def read_file(self, file_path):
        """Restore transactions from a JSON Journal object."""
        try:
            payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            transactions = payload.get("transactions", [])
            if not isinstance(transactions, list):
                raise ValueError("transactions must be a list")
        except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
            transactions = []
        self._rows.clear()
        for transaction in transactions:
            if not isinstance(transaction, dict):
                continue
            try:
                value = float(transaction["value"])
                description = str(transaction.get("description", "Transaction")).strip() or "Transaction"
            except (KeyError, TypeError, ValueError):
                continue
            self._rows.append((value, description))
        self._refresh_rows()

    def write_file(self, file_path):
        """Save transactions as a JSON Journal object."""
        Path(file_path).write_text(json.dumps({"transactions": [{"value": value, "description": description} for value, description in self._rows]}, sort_keys=True) + "\n", encoding="utf-8")
