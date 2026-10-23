"""Finance ledger, view periods and budgets, independent of GTK.

The Journal payload is the GTK3 Finance format (sugarlabs/finance-activity,
finance.py), so objects open in either version::

    {"next_id": 3,
     "transactions": [{"id", "name", "type": "credit"|"debit", "amount",
                       "date": <proleptic ordinal>, "category"}],
     "budgets": {"<category>": {"amount": <monthly amount>}}}

Unknown top-level keys are kept, so a newer payload survives a resave.
"""

import copy
import datetime

DAY, WEEK, MONTH, YEAR, FOREVER = range(5)
PERIOD_NAMES = ("Day", "Week", "Month", "Year", "Forever")
# GTK3 budgets are monthly; other periods scale them the same way.
BUDGET_SCALE = {DAY: 1 / 30.0, WEEK: 1 / 4.0, MONTH: 1.0, YEAR: 12.0, FOREVER: None}


def period_start(period, today):
    if period == DAY:
        return today
    if period == WEEK:
        return today - datetime.timedelta(days=today.weekday())
    if period == MONTH:
        return today.replace(day=1)
    if period == YEAR:
        return datetime.date(today.year, 1, 1)
    return datetime.date(1900, 1, 1)


def next_period(period, start):
    if period == DAY:
        return start + datetime.timedelta(days=1)
    if period == WEEK:
        return start + datetime.timedelta(days=7)
    if period == MONTH:
        return datetime.date(start.year + start.month // 12, start.month % 12 + 1, 1)
    if period == YEAR:
        return datetime.date(start.year + 1, 1, 1)
    return datetime.date.max


def prev_period(period, start):
    if period == DAY:
        return start - datetime.timedelta(days=1)
    if period == WEEK:
        return start - datetime.timedelta(days=7)
    if period == MONTH:
        return datetime.date(start.year - (start.month == 1), (start.month - 2) % 12 + 1, 1)
    if period == YEAR:
        return datetime.date(start.year - 1, 1, 1)
    return start


def period_label(period, start):
    if period == DAY:
        return start.strftime("%A %d %B %Y")
    if period == WEEK:
        return "Week of %s" % start.strftime("%d %B %Y")
    if period == MONTH:
        return start.strftime("%B %Y")
    if period == YEAR:
        return str(start.year)
    return "All transactions"


def _transaction(raw):
    if not isinstance(raw, dict):
        raise ValueError("transaction must be an object")
    kind = raw.get("type")
    if kind not in ("credit", "debit"):
        raise ValueError("transaction type must be credit or debit")
    amount, date = raw.get("amount"), raw.get("date")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount < 0:
        raise ValueError("transaction amount must be a non-negative number")
    if isinstance(date, bool) or not isinstance(date, int) or date < 1:
        raise ValueError("transaction date must be a day ordinal")
    if not isinstance(raw.get("id"), int) or not isinstance(raw.get("name", ""), str) \
            or not isinstance(raw.get("category", ""), str):
        raise ValueError("transaction id, name or category is malformed")
    return raw


class Ledger:
    def __init__(self, data=None, today=None):
        self.data = data if data is not None else {"next_id": 0, "transactions": [], "budgets": {}}
        self.today = today or datetime.date.today()
        self.period = MONTH
        self.start = period_start(MONTH, self.today)
        self._undo, self._redo = [], []

    # Journal payload

    @classmethod
    def from_payload(cls, payload, today=None):
        if not isinstance(payload, dict):
            raise ValueError("Finance payload must be an object")
        today = today or datetime.date.today()
        transactions = payload.get("transactions", [])
        if not isinstance(transactions, list):
            raise ValueError("transactions must be a list")
        if "next_id" not in payload and all(isinstance(t, dict) and "value" in t for t in transactions):
            # GTK4 Finance 1: signed values and descriptions, no dates.
            ledger = cls(today=today)
            for t in transactions:
                value = t["value"]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError("transaction value must be a number")
                ledger.add(str(t.get("description", "")), "credit" if value >= 0 else "debit",
                           abs(value), "", today, record=False)
            return ledger
        data = dict(payload)
        data["transactions"] = [_transaction(t) for t in transactions]
        budgets = data.setdefault("budgets", {})
        if not isinstance(budgets, dict) or not all(
                isinstance(b, dict) and isinstance(b.get("amount"), (int, float))
                and not isinstance(b.get("amount"), bool) for b in budgets.values()):
            raise ValueError("budgets must map categories to amounts")
        ids = [t["id"] for t in data["transactions"]]
        if len(set(ids)) != len(ids):
            raise ValueError("transaction ids repeat")
        next_id = data.get("next_id", 0)
        if isinstance(next_id, bool) or not isinstance(next_id, int):
            raise ValueError("next_id must be an integer")
        data["next_id"] = max([next_id] + [i + 1 for i in ids])
        return cls(data, today)

    def to_payload(self):
        return self.data

    # Edits (each one can be undone)

    def _checkpoint(self):
        self._undo.append(copy.deepcopy(self.data))
        self._redo.clear()

    def add(self, name, kind, amount, category, date, record=True):
        if kind not in ("credit", "debit"):
            raise ValueError("kind must be credit or debit")
        if amount < 0:
            raise ValueError("amount must not be negative")
        name, category = name.strip(), category.strip()
        if not category and name:
            # As in GTK3: reuse the category last given to this description.
            category = next((t["category"] for t in reversed(self.data["transactions"])
                             if t["name"] == name and t["category"]), "")
        if record:
            self._checkpoint()
        t = {"id": self.data["next_id"], "name": name, "type": kind, "amount": amount,
             "date": date.toordinal(), "category": category}
        self.data["next_id"] += 1
        self.data["transactions"].append(t)
        return t

    def remove(self, transaction_id):
        self._checkpoint()
        self.data["transactions"] = [t for t in self.data["transactions"] if t["id"] != transaction_id]

    def set_budget(self, category, amount):
        self._checkpoint()
        if amount is None:
            self.data["budgets"].pop(category, None)
        else:
            if amount < 0:
                raise ValueError("budget must not be negative")
            self.data["budgets"][category] = {"amount": amount}

    def undo(self):
        if not self._undo:
            return False
        self._redo.append(self.data)
        self.data = self._undo.pop()
        return True

    def redo(self):
        if not self._redo:
            return False
        self._undo.append(self.data)
        self.data = self._redo.pop()
        return True

    @property
    def can_undo(self):
        return bool(self._undo)

    @property
    def can_redo(self):
        return bool(self._redo)

    # Views

    def set_period(self, period):
        self.period = period
        self.start = period_start(period, self.today)

    def step(self, direction):
        if self.period == FOREVER:
            return
        if direction == 0:
            self.start = period_start(self.period, self.today)
        elif direction > 0:
            self.start = next_period(self.period, self.start)
        else:
            self.start = prev_period(self.period, self.start)

    @property
    def label(self):
        return period_label(self.period, self.start)

    def visible(self):
        if self.period == FOREVER:
            rows = list(self.data["transactions"])
        else:
            low = self.start.toordinal()
            high = next_period(self.period, self.start).toordinal()
            rows = [t for t in self.data["transactions"] if low <= t["date"] < high]
        return sorted(rows, key=lambda t: (t["date"], t["id"]))

    def totals(self, rows=None):
        rows = self.visible() if rows is None else rows
        income = sum(t["amount"] for t in rows if t["type"] == "credit")
        expenses = sum(t["amount"] for t in rows if t["type"] == "debit")
        return income, expenses

    def by_category(self, kind="debit"):
        totals = {}
        for t in self.visible():
            if t["type"] == kind:
                totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]
        return dict(sorted(totals.items(), key=lambda item: -item[1]))

    def categories(self):
        return sorted({t["category"] for t in self.data["transactions"] if t["category"]})

    def budget_rows(self):
        """(category, spent, budget for this period or None, status) rows.

        Status is ``over`` when spending passed the budget, ``ahead`` when it
        is running ahead of the time elapsed in the period, else ``ok``.
        """
        spent = self.by_category("debit")
        scale = BUDGET_SCALE[self.period]
        elapsed = None
        if self.period not in (DAY, FOREVER):
            end = next_period(self.period, self.start)
            elapsed = (self.today - self.start).days / max(1, (end - self.start).days)
        rows = []
        for category in sorted(set(spent) | set(self.data["budgets"])):
            entry = self.data["budgets"].get(category)
            budget = None if entry is None or scale is None else entry["amount"] * scale
            used = spent.get(category, 0)
            status = "ok"
            if budget is not None:
                ratio = used / budget if budget else (10.0 if used else 0.0)
                if ratio > 1:
                    status = "over"
                elif elapsed is not None and 0 < elapsed < ratio:
                    status = "ahead"
            rows.append((category, used, budget, status))
        return rows
