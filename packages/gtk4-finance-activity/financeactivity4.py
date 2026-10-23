"""Native GTK4 Finance Activity.

A port of GTK3 Finance (sugarlabs/finance-activity): a dated, categorised
register, monthly budgets per category, a category chart, view periods
(day to forever) and undo/redo. The ledger lives in :mod:`finance_model`
and keeps the GTK3 Journal format.
"""

import datetime
import json
import math
from pathlib import Path

from gi.repository import Gdk, Gtk
from sugar4.activity import SimpleActivity

from finance_csv import read_csv, write_csv
from finance_model import FOREVER, MONTH, PERIOD_NAMES, Ledger

PALETTE = ((0.18, 0.53, 0.74), (0.85, 0.37, 0.28), (0.30, 0.62, 0.36), (0.93, 0.68, 0.20),
           (0.55, 0.38, 0.68), (0.20, 0.65, 0.65), (0.75, 0.42, 0.58), (0.50, 0.50, 0.50))
STATUS_TEXT = {"over": "over budget", "ahead": "ahead of schedule", "ok": "on track"}


def money(amount):
    return "{:,.2f}".format(amount)


def category_color(category, categories):
    return PALETTE[categories.index(category) % len(PALETTE)] if category in categories else PALETTE[-1]


class FinanceActivity(SimpleActivity):
    def __init__(self, activity_handle=None):
        super().__init__(activity_handle)
        self.set_title("Finance")
        self.ledger = Ledger()
        self._build()
        self._refresh("Ready")

    # Layout

    def _button(self, label, tip, handler, *args):
        button = Gtk.Button(label=label)
        button.set_tooltip_text(tip)
        button.connect("clicked", handler, *args)
        return button

    def _entry(self, name, placeholder="", width=None):
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder or name)
        entry.update_property([Gtk.AccessibleProperty.LABEL], [name])
        if width:
            entry.set_width_chars(width)
        return entry

    def _build(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(18); root.set_margin_bottom(18)
        root.set_margin_start(26); root.set_margin_end(26)
        root.update_property([Gtk.AccessibleProperty.LABEL], ["Finance"])

        header = Gtk.Box(spacing=10)
        title = Gtk.Label(label="Finance", xalign=0)
        title.add_css_class("title-1")
        title.set_hexpand(True)
        header.append(title)
        self.stack = Gtk.Stack()
        switcher = Gtk.StackSwitcher(stack=self.stack)
        header.append(switcher)
        self.undo_button = self._button("Undo", "Undo the last change", self._undo)
        self.redo_button = self._button("Redo", "Redo the change you undid", self._redo)
        header.append(self.undo_button)
        header.append(self.redo_button)
        root.append(header)

        period_bar = Gtk.Box(spacing=8)
        self.period = Gtk.DropDown.new_from_strings(list(PERIOD_NAMES))
        self.period.set_selected(MONTH)
        self.period.update_property([Gtk.AccessibleProperty.LABEL], ["View period"])
        self.period.connect("notify::selected", self._period_changed)
        period_bar.append(self.period)
        self.prev_button = self._button("Previous", "Show the previous period", self._step, -1)
        self.this_button = self._button("Today", "Show the period that contains today", self._step, 0)
        self.next_button = self._button("Next", "Show the next period", self._step, 1)
        for button in (self.prev_button, self.this_button, self.next_button):
            period_bar.append(button)
        self.period_label = Gtk.Label(xalign=0)
        self.period_label.add_css_class("heading")
        self.period_label.set_hexpand(True)
        period_bar.append(self.period_label)
        self.balance = Gtk.Label(xalign=1)
        self.balance.add_css_class("heading")
        self.balance.update_property([Gtk.AccessibleProperty.LABEL], ["Period totals"])
        period_bar.append(self.balance)
        root.append(period_bar)

        self.stack.add_titled(self._register_page(), "register", "Register")
        self.stack.add_titled(self._budget_page(), "budget", "Budget")
        self.stack.add_titled(self._chart_page(), "chart", "Chart")
        self.stack.set_vexpand(True)
        root.append(self.stack)

        self.status = Gtk.Label(xalign=0, wrap=True)
        self.status.add_css_class("dim-label")
        self.status.update_property([Gtk.AccessibleProperty.LABEL], ["Finance status"])
        root.append(self.status)
        self.set_canvas(root)

        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"entry { min-height: 40px; } button { min-height: 40px; border-radius: 19px; }"
            b" frame.finance-pane { border: 1px solid #8aa8b8; border-radius: 10px; padding: 10px; }"
            b" listboxrow { padding: 6px 10px; } label.credit { color: #2e7d4f; }"
            b" label.debit { color: #b5442f; } progressbar.over progress { background: #d9534f; }"
            b" progressbar.ahead progress { background: #e0b030; }")
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _register_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        form = Gtk.Grid(column_spacing=10, row_spacing=4)
        self.description = self._entry("Description")
        self.description.set_hexpand(True)
        self.category = self._entry("Category", "Category, e.g. Food", 16)
        self.amount = self._entry("Amount", "0.00", 10)
        self.amount.set_input_purpose(Gtk.InputPurpose.NUMBER)
        self.date = self._entry("Date", "YYYY-MM-DD", 12)
        self.date.set_text(self.ledger.today.isoformat())
        for column, (label, entry) in enumerate((("Description", self.description),
                                                 ("Category", self.category),
                                                 ("Amount", self.amount), ("Date", self.date))):
            form.attach(Gtk.Label(label=label, xalign=0), column, 0, 1, 1)
            form.attach(entry, column, 1, 1, 1)
        self.amount.connect("activate", self._add, "debit")
        actions = Gtk.Box(spacing=8)
        actions.set_halign(Gtk.Align.END)
        actions.append(self._button("Add income", "Record money coming in", self._add, "credit"))
        actions.append(self._button("Add expense", "Record money going out", self._add, "debit"))
        actions.append(self._button("Import CSV", "Add transactions from a CSV file", self._import_csv))
        actions.append(self._button("Export CSV", "Save every transaction as a CSV file", self._export_csv))
        form.attach(actions, 0, 2, 4, 1)
        frame = Gtk.Frame(label="New transaction")
        frame.add_css_class("finance-pane")
        frame.set_child(form)
        page.append(frame)

        self.rows = Gtk.ListBox()
        self.rows.set_selection_mode(Gtk.SelectionMode.NONE)
        self.rows.update_property([Gtk.AccessibleProperty.LABEL], ["Transactions"])
        self.empty = Gtk.Label(label="No transactions in this period.", wrap=True)
        self.empty.add_css_class("dim-label")
        self.rows.set_placeholder(self.empty)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.rows)
        frame = Gtk.Frame(label="Transactions")
        frame.add_css_class("finance-pane")
        frame.set_child(scroll)
        page.append(frame)
        return page

    def _budget_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        help_text = Gtk.Label(
            label="Set a monthly budget for each expense category. Other periods scale it: "
                  "a week is a quarter of a month, a year is twelve months.",
            xalign=0, wrap=True)
        help_text.add_css_class("dim-label")
        page.append(help_text)
        form = Gtk.Box(spacing=8)
        self.budget_category = self._entry("Budget category", "Category", 16)
        self.budget_amount = self._entry("Monthly budget", "Monthly amount", 12)
        self.budget_amount.connect("activate", self._set_budget_from_form)
        form.append(self.budget_category)
        form.append(self.budget_amount)
        form.append(self._button("Set budget", "Set this category's monthly budget",
                                 self._set_budget_from_form))
        page.append(form)
        self.budgets = Gtk.ListBox()
        self.budgets.set_selection_mode(Gtk.SelectionMode.NONE)
        self.budgets.update_property([Gtk.AccessibleProperty.LABEL], ["Budgets"])
        placeholder = Gtk.Label(label="No expense categories yet.")
        placeholder.add_css_class("dim-label")
        self.budgets.set_placeholder(placeholder)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        scroll.set_child(self.budgets)
        page.append(scroll)
        return page

    def _chart_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bar = Gtk.Box(spacing=8)
        self.chart_kind = Gtk.DropDown.new_from_strings(["Expenses", "Income"])
        self.chart_kind.update_property([Gtk.AccessibleProperty.LABEL], ["Chart shows"])
        self.chart_kind.connect("notify::selected", lambda *_: self._refresh_chart())
        bar.append(self.chart_kind)
        self.chart_summary = Gtk.Label(xalign=0, wrap=True)
        self.chart_summary.set_hexpand(True)
        self.chart_summary.update_property([Gtk.AccessibleProperty.LABEL], ["Chart summary"])
        bar.append(self.chart_summary)
        page.append(bar)
        self.chart = Gtk.DrawingArea(vexpand=True, hexpand=True)
        self.chart.set_draw_func(self._draw_chart)
        self.chart.update_property([Gtk.AccessibleProperty.LABEL], ["Category chart"])
        page.append(self.chart)
        return page

    # Refresh

    def _refresh(self, message=None):
        ledger = self.ledger
        self.period_label.set_text(ledger.label)
        for button in (self.prev_button, self.this_button, self.next_button):
            button.set_sensitive(ledger.period != FOREVER)
        income, expenses = ledger.totals()
        self.balance.set_text("In %s · Out %s · Net %s" % (money(income), money(expenses),
                                                           money(income - expenses)))
        self.undo_button.set_sensitive(ledger.can_undo)
        self.redo_button.set_sensitive(ledger.can_redo)
        self._refresh_register()
        self._refresh_budgets()
        self._refresh_chart()
        if message:
            self.status.set_text(message)

    def _refresh_register(self):
        self.rows.remove_all()
        for t in self.ledger.visible():
            row = Gtk.Box(spacing=12)
            date = datetime.date.fromordinal(t["date"]).isoformat()
            name = t["name"] or ("Income" if t["type"] == "credit" else "Expense")
            for text, expand, xalign in ((date, False, 0), (name, True, 0),
                                         (t["category"] or "—", False, 0)):
                label = Gtk.Label(label=text, xalign=xalign, hexpand=expand)
                label.set_width_chars(12 if not expand else -1)
                row.append(label)
            sign = "+" if t["type"] == "credit" else "−"
            amount = Gtk.Label(label=sign + money(t["amount"]), xalign=1)
            amount.add_css_class(t["type"])
            amount.set_width_chars(12)
            row.append(amount)
            remove = self._button("Remove", "Remove this transaction", self._remove, t["id"])
            remove.update_property([Gtk.AccessibleProperty.LABEL],
                                   ["Remove %s %s %s" % (date, name, money(t["amount"]))])
            row.append(remove)
            self.rows.append(row)

    def _refresh_budgets(self):
        self.budgets.remove_all()
        for category, spent, budget, status in self.ledger.budget_rows():
            name = category or "Uncategorised"
            row = Gtk.Box(spacing=12)
            label = Gtk.Label(label=name, xalign=0)
            label.set_width_chars(16)
            row.append(label)
            bar = Gtk.ProgressBar(hexpand=True, valign=Gtk.Align.CENTER, show_text=True)
            if budget is None:
                text = "%s spent, no budget" % money(spent)
                bar.set_fraction(0)
            else:
                text = "%s of %s, %s" % (money(spent), money(budget), STATUS_TEXT[status])
                bar.set_fraction(min(1.0, spent / budget) if budget else 1.0)
                bar.add_css_class(status)
            bar.set_text(text)
            bar.update_property([Gtk.AccessibleProperty.LABEL], ["%s budget: %s" % (name, text)])
            row.append(bar)
            entry = self._entry("Monthly budget for %s" % name, "Monthly", 10)
            stored = self.ledger.data["budgets"].get(category)
            if stored:
                entry.set_text("%.2f" % stored["amount"])
            entry.connect("activate", self._set_budget, category)
            row.append(entry)
            self.budgets.append(row)

    def _refresh_chart(self):
        kind = "debit" if self.chart_kind.get_selected() == 0 else "credit"
        totals = self.ledger.by_category(kind)
        if totals:
            total = sum(totals.values())
            self.chart_summary.set_text(", ".join(
                "%s %s (%d%%)" % (c or "Uncategorised", money(v), round(100 * v / total) if total else 0)
                for c, v in totals.items()))
        else:
            self.chart_summary.set_text("No %s in this period." % ("expenses" if kind == "debit" else "income"))
        self.chart.queue_draw()

    def _draw_chart(self, _area, cr, width, height):
        kind = "debit" if self.chart_kind.get_selected() == 0 else "credit"
        totals = self.ledger.by_category(kind)
        total = sum(totals.values())
        if not total:
            return
        categories = self.ledger.categories()
        radius = min(width * 0.3, height / 2 - 20)
        cx, cy = radius + 30, height / 2
        angle = -math.pi / 2
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(15)
        for index, (category, value) in enumerate(totals.items()):
            sweep = 2 * math.pi * value / total
            cr.set_source_rgb(*category_color(category, categories))
            cr.move_to(cx, cy)
            cr.arc(cx, cy, radius, angle, angle + sweep)
            cr.close_path()
            cr.fill()
            angle += sweep
            y = 40 + index * 30
            cr.rectangle(cx + radius + 40, y - 14, 18, 18)
            cr.fill()
            cr.set_source_rgb(0.15, 0.2, 0.22)
            cr.move_to(cx + radius + 66, y)
            cr.show_text("%s  %s" % (category or "Uncategorised", money(value)))

    # Actions

    def _add(self, _widget, kind):
        try:
            amount = float(self.amount.get_text().strip().replace(",", ""))
            if amount < 0 or not math.isfinite(amount):
                raise ValueError
        except ValueError:
            self.status.set_text("Enter an amount, like 12.50")
            self.amount.grab_focus()
            return
        try:
            date = datetime.date.fromisoformat(self.date.get_text().strip())
        except ValueError:
            self.status.set_text("Enter the date as YYYY-MM-DD")
            self.date.grab_focus()
            return
        t = self.ledger.add(self.description.get_text(), kind, amount, self.category.get_text(), date)
        self.description.set_text(""); self.category.set_text(""); self.amount.set_text("")
        self.description.grab_focus()
        word = "Income" if kind == "credit" else "Expense"
        self._refresh("%s added: %s %s%s" % (word, t["name"] or word.lower(), money(amount),
                                              " in %s" % t["category"] if t["category"] else ""))

    def _remove(self, _button, transaction_id):
        self.ledger.remove(transaction_id)
        self._refresh("Transaction removed")

    def _set_budget(self, entry, category):
        text = entry.get_text().strip().replace(",", "")
        try:
            amount = float(text) if text else None
            if amount is not None and (amount < 0 or not math.isfinite(amount)):
                raise ValueError
        except ValueError:
            self.status.set_text("Enter a monthly budget, like 50")
            return
        self.ledger.set_budget(category, amount)
        name = category or "Uncategorised"
        self._refresh("Budget for %s: %s a month" % (name, money(amount)) if amount is not None
                      else "Budget for %s removed" % name)

    def _set_budget_from_form(self, _widget):
        category = self.budget_category.get_text().strip()
        if not category:
            self.status.set_text("Name the category to budget")
            return
        self._set_budget(self.budget_amount, category)
        self.budget_category.set_text(""); self.budget_amount.set_text("")

    def _period_changed(self, dropdown, _pspec):
        self.ledger.set_period(dropdown.get_selected())
        self._refresh()

    def _step(self, _button, direction):
        self.ledger.step(direction)
        self._refresh()

    def _undo(self, _button):
        if self.ledger.undo():
            self._refresh("Undone")

    def _redo(self, _button):
        if self.ledger.redo():
            self._refresh("Redone")

    def _import_csv(self, _button):
        Gtk.FileDialog(title="Import Finance CSV").open(self, None, self._import_csv_chosen)

    def _import_csv_chosen(self, dialog, result):
        try:
            file_obj = dialog.open_finish(result)
            path = file_obj.get_path() if file_obj is not None else None
            if not path:
                return
            rows = read_csv(path, self.ledger.today)
        except Exception as error:
            self.status.set_text("Import failed: %s" % error)
            return
        self.ledger._checkpoint()
        for name, kind, amount, category, date in rows:
            self.ledger.add(name, kind, amount, category, date, record=False)
        self._refresh("Imported %d transaction%s" % (len(rows), "" if len(rows) == 1 else "s"))

    def _export_csv(self, _button):
        Gtk.FileDialog(title="Export Finance CSV", initial_name="finance.csv").save(
            self, None, self._export_csv_chosen)

    def _export_csv_chosen(self, dialog, result):
        try:
            file_obj = dialog.save_finish(result)
            path = file_obj.get_path() if file_obj is not None else None
            if not path:
                return
            write_csv(path, sorted(self.ledger.data["transactions"], key=lambda t: t["date"]))
        except Exception as error:
            self.status.set_text("Export failed: %s" % error)
            return
        self.status.set_text("Exported %d transactions" % len(self.ledger.data["transactions"]))

    # Journal

    def read_file(self, file_path):
        """Restore a GTK3 or GTK4 Finance ledger; anything else raises."""
        payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
        ledger = Ledger.from_payload(payload)
        ledger.set_period(self.ledger.period)
        self.ledger = ledger
        self._refresh("Restored %d transactions" % len(ledger.data["transactions"]))

    def write_file(self, file_path):
        """Save the ledger in the GTK3 Finance format."""
        if self.metadata is not None:
            self.metadata["mime_type"] = "text/plain"
        Path(file_path).write_text(json.dumps(self.ledger.to_payload(), sort_keys=True) + "\n",
                                   encoding="utf-8")
