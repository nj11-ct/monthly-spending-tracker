from datetime import datetime, date
import calendar


def parse_month(month_str: str | None) -> date:
    if not month_str:
        today = datetime.today()
        return date(today.year, today.month, 1)
    year, mon = (int(x) for x in month_str.split("-"))
    return date(year, mon, 1)


def month_bounds(first_of_month: date):
    y, m = first_of_month.year, first_of_month.month
    last = calendar.monthrange(y, m)[1]
    return (first_of_month, date(y, m, last))


def month_str(dt: date) -> str:
    return dt.strftime("%Y-%m")


def prev_month_str(month_str_input: str) -> str:
    d = parse_month(month_str_input)
    y, m = (d.year, d.month - 1)
    if m == 0:
        y -= 1
        m = 12
    return f"{y:04d}-{m:02d}"


def next_month_str(month_str_input: str) -> str:
    d = parse_month(month_str_input)
    y, m = (d.year, d.month + 1)
    if m == 13:
        y += 1
        m = 1
    return f"{y:04d}-{m:02d}"
