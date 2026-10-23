import datetime
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "packages/gtk4-finance-activity"
sys.path.insert(0, str(PACKAGE))
from finance_csv import read_csv, write_csv  # noqa: E402
from finance_model import DAY, FOREVER, WEEK, YEAR, Ledger  # noqa: E402
from gtk4_activity_harness import needs_gtk4, run  # noqa: E402

TODAY = datetime.date(2026, 10, 22)


def ledger():
    book = Ledger(today=TODAY)
    book.add("Pay", "credit", 1000, "Work", datetime.date(2026, 10, 1))
    book.add("Bread", "debit", 4.5, "Food", datetime.date(2026, 10, 3))
    book.add("Bus pass", "debit", 50, "Transport", datetime.date(2026, 9, 20))
    return book


def test_periods_filter_the_register():
    book = ledger()
    assert book.label == "October 2026" and book.totals() == (1000, 4.5)
    book.step(-1)
    assert book.label == "September 2026" and book.totals() == (0, 50)
    book.set_period(YEAR)
    assert book.totals() == (1000, 54.5)
    book.set_period(FOREVER)
    assert len(book.visible()) == 3
    book.set_period(WEEK)
    assert book.start == datetime.date(2026, 10, 19)
    book.set_period(DAY)
    assert book.visible() == []


def test_monthly_budgets_scale_and_report_status():
    book = ledger()
    book.set_budget("Food", 4)
    assert book.budget_rows()[0] == ("Food", 4.5, 4.0, "over")
    book.set_budget("Food", 5)   # 90% spent, 68% of October gone
    assert book.budget_rows()[0][3] == "ahead"
    book.set_period(YEAR)
    assert book.budget_rows()[0][2] == 60.0
    book.set_period(WEEK)
    assert book.budget_rows()[0][2] == 1.25


def test_description_reuses_its_last_category():
    book = ledger()
    assert book.add("Bread", "debit", 3, "", TODAY)["category"] == "Food"


def test_undo_and_redo():
    book = ledger()
    book.set_budget("Food", 10)
    book.remove(0)
    assert book.undo() and len(book.data["transactions"]) == 3
    assert book.undo() and book.data["budgets"] == {}
    assert book.redo() and book.data["budgets"] == {"Food": {"amount": 10}}


def test_gtk3_payload_round_trips_and_keeps_unknown_keys():
    payload = {"next_id": 2, "budgets": {"Food": {"amount": 20.0}}, "future": [1],
               "transactions": [{"id": 0, "name": "Rice", "type": "debit", "amount": 2.5,
                                 "date": TODAY.toordinal(), "category": "Food"},
                                {"id": 1, "name": "Gift", "type": "credit", "amount": 10,
                                 "date": TODAY.toordinal(), "category": ""}]}
    book = Ledger.from_payload(json.loads(json.dumps(payload)), today=TODAY)
    assert book.totals() == (10, 2.5)
    assert book.to_payload() == payload


def test_gtk4_finance_1_payload_still_opens():
    book = Ledger.from_payload({"transactions": [{"value": -5.0, "description": "Pens"}]},
                               today=TODAY)
    assert book.visible()[0]["name"] == "Pens" and book.totals() == (0, 5.0)


@pytest.mark.parametrize("payload", [
    [], {"transactions": {}}, {"next_id": 1, "transactions": [{"id": 0, "type": "gift"}]},
    {"next_id": 0, "transactions": [], "budgets": {"Food": 3}},
])
def test_malformed_payloads_raise(payload):
    with pytest.raises(ValueError):
        Ledger.from_payload(payload)


def test_csv_keeps_dates_and_categories(tmp_path):
    book = ledger()
    path = tmp_path / "finance.csv"
    write_csv(path, book.data["transactions"])
    assert read_csv(path) == [("Pay", "credit", 1000.0, "Work", datetime.date(2026, 10, 1)),
                              ("Bread", "debit", 4.5, "Food", datetime.date(2026, 10, 3)),
                              ("Bus pass", "debit", 50.0, "Transport", datetime.date(2026, 9, 20))]


@needs_gtk4
def test_activity_records_expense_and_budget(tmp_path):
    out = run("gtk4-finance-activity", f"""
        from financeactivity4 import FinanceActivity
        activity = FinanceActivity(None)
        activity.description.set_text("Bread")
        activity.category.set_text("Food")
        activity.amount.set_text("4.50")
        button(activity, "Add expense").emit("clicked")
        activity.budget_category.set_text("Food")
        activity.budget_amount.set_text("10")
        button(activity, "Set budget").emit("clicked")
        print("status", activity.status.get_text())
        activity.write_file({str(tmp_path / 'finance.json')!r})
        restored = FinanceActivity(None)
        restored.read_file({str(tmp_path / 'finance.json')!r})
        print("budget", restored.ledger.budget_rows()[0][:3])
        print("chart", restored.chart_summary.get_text())
        try:
            open({str(tmp_path / 'bad')!r}, "wb").write(b"\\xff\\xfe not json")
            restored.read_file({str(tmp_path / 'bad')!r})
        except ValueError:
            print("refused")
    """)
    assert "status Budget for Food: 10.00 a month" in out
    assert "budget ('Food', 4.5, 10.0)" in out
    assert "chart Food 4.50 (100%)" in out
    assert "refused" in out


def test_bundle_is_registered():
    info = (PACKAGE / "activity/activity.info").read_text()
    assert "bundle_id = org.laptop.community.Finance" in info
    assert "sugar-activity4 financeactivity4.FinanceActivity" in info
    assert "org.laptop.community.Finance" in (ROOT / "scripts/sugar-gtk4-activity-matrix.sh").read_text()
    assert "gtk4-finance-activity" in (ROOT / "scripts/sugar-gtk4-dev-sync.sh").read_text()
    assert "gtk4-finance-activity" in (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
