"""Reads exams from MongoDB and works out each exam's status from today's date."""
from datetime import date, datetime

from db import exams_collection


def to_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def fmt(d):
    # Avoids %-d, which doesn't work on Windows
    return f"{d.day} {d.strftime('%b %Y')}"


def _prepare(exam, today):
    start, end = to_date(exam.get("apply_start")), to_date(exam.get("apply_end"))
    exam["applications_open"] = bool(
        end and today <= end and (start is None or today >= start)
    )

    if end is None:
        exam["apply_text"] = "Application dates not confirmed"
    elif today > end:
        exam["apply_text"] = f"Applications closed on {fmt(end)}"
    elif start and today < start:
        exam["apply_text"] = f"Applications open {fmt(start)} to {fmt(end)}"
    else:
        exam["apply_text"] = f"Applications open until {fmt(end)}"

    all_dates, rows = [], []
    for stage in exam.get("stages", []):
        dates = [to_date(x) for x in stage.get("dates", [])]
        all_dates += dates
        rows.append({
            "name": stage["name"],
            "text": ", ".join(fmt(d) for d in dates) if dates else "Date not announced",
            "tentative": bool(dates) and stage.get("tentative", False),
            "done": bool(dates) and max(dates) < today,
        })
    exam["stage_rows"] = rows

    future = [d for d in all_dates if d >= today]
    next_date = min(future) if future else None
    exam["next_date"] = next_date
    exam["next_date_text"] = fmt(next_date) if next_date else None
    exam["days_left"] = (next_date - today).days if next_date else None

    if exam["applications_open"]:
        exam["status"], exam["sort_group"] = "Applications open", 0
    elif next_date:
        has_past = any(d < today for d in all_dates)
        exam["status"] = "In progress" if has_past else "Upcoming"
        exam["sort_group"] = 1
    elif all_dates:
        exam["status"], exam["sort_group"] = "Exam stages finished", 3
    else:
        exam["status"], exam["sort_group"] = "Dates not announced", 2
    return exam


def get_exams(today=None):
    today = today or date.today()
    exams = [_prepare(e, today) for e in exams_collection.find({}, {"_id": 0})]
    exams.sort(key=lambda e: (e["sort_group"], e["next_date"] or date.max, e["name"]))
    return exams
