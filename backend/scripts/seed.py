import argparse
from datetime import date, datetime
from decimal import Decimal

from app.core.database import SessionLocal, engine
from app.core import models
from app.core.utils import parse_month, month_bounds

# Ensure tables exist (in case seed is run before server startup)
models.Base.metadata.create_all(bind=engine)

SAMPLE_DATA = {
    "income": [
        {"category": "salary", "amount": Decimal("5000.00"), "description": "Monthly salary"},
        {"category": "carryover", "amount": Decimal("6000.00"), "description": "Carryover"},
    ],
    "expense": [
        {"category": "groceries", "amount": Decimal("120.50"), "description": "Groceries"},
        {"category": "groceries", "amount": Decimal("45.00"), "description": "Snacks"},
        {"category": "eating_out", "amount": Decimal("4500.00"), "description": "Dining"},
    ],
}


def seed_month(month_str: str | None):
    first = parse_month(month_str)
    start, end = month_bounds(first)
    mid = date(first.year, first.month, min(24, end.day))

    with SessionLocal() as db:
        inserted = 0
        # Income: place entries on first and last day
        income_dates = [end, first]
        for i, item in enumerate(SAMPLE_DATA["income"]):
            tx_date = income_dates[i % len(income_dates)]
            exists = (
                db.query(models.Transaction)
                .filter(
                    models.Transaction.date == tx_date,
                    models.Transaction.type == "income",
                    models.Transaction.category == item["category"],
                    models.Transaction.amount == item["amount"],
                )
                .first()
            )
            if exists:
                continue
            db.add(
                models.Transaction(
                    date=tx_date,
                    type="income",
                    category=item["category"],
                    amount=item["amount"],
                    description=item["description"],
                )
            )
            inserted += 1

        # Expenses: scatter
        expense_dates = [mid, end, first]
        for i, item in enumerate(SAMPLE_DATA["expense"]):
            tx_date = expense_dates[i % len(expense_dates)]
            exists = (
                db.query(models.Transaction)
                .filter(
                    models.Transaction.date == tx_date,
                    models.Transaction.type == "expense",
                    models.Transaction.category == item["category"],
                    models.Transaction.amount == item["amount"],
                )
                .first()
            )
            if exists:
                continue
            db.add(
                models.Transaction(
                    date=tx_date,
                    type="expense",
                    category=item["category"],
                    amount=item["amount"],
                    description=item["description"],
                )
            )
            inserted += 1

        db.commit()
        return inserted


def main():
    parser = argparse.ArgumentParser(description="Seed demo transactions for a month")
    parser.add_argument("--month", help="Target month YYYY-MM (default: current month)", default=None)
    args = parser.parse_args()
    inserted = seed_month(args.month)
    print(f"Inserted {inserted} rows for month {args.month or datetime.today().strftime('%Y-%m')}")


if __name__ == "__main__":
    main()
