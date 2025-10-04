# tools/schedule.py
# Simple weekly packer for PO CSVs (120 t/week default).
# No AI here: just read CSV, pack into ISO weeks, add feasibility notes.

from datetime import date, timedelta
import csv

CAPACITY_T_PER_WEEK = 120.0  # default shop capacity

# ---------- ISO week helpers ----------
def parse_week_str(week_str: str):
    # "YYYY-Www" -> (year, week)
    year, w = week_str.split("-W")
    return int(year), int(w)

def week_to_monday(year: int, week: int) -> date:
    return date.fromisocalendar(year, week, 1)  # Monday

def monday_to_week_str(monday: date) -> str:
    y, w, _ = monday.isocalendar()
    return f"{y:04d}-W{w:02d}"

def advance_week(year: int, week: int):
    mon = week_to_monday(year, week) + timedelta(days=7)
    y, w, _ = mon.isocalendar()
    return y, w

def week_leq(y1: int, w1: int, y2: int, w2: int) -> bool:
    return (y1, w1) <= (y2, w2)

# ---------- core ----------
def read_po_csv(path: str):
    """Return list of dicts: {po_id, weight_tonnes, due_date}"""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "po_id": r["po_id"].strip(),
                "weight_tonnes": float(r["weight_tonnes"]),
                "due_date": r["due_date"].strip(),  # "YYYY-MM-DD"
            })
    return rows

def schedule_rows(rows, start_week: str, capacity_t_per_week: float = CAPACITY_T_PER_WEEK):
    """Greedy pack: don’t split items; if a PO pushes past capacity, move to next week."""
    cur_year, cur_week = parse_week_str(start_week)
    used = 0.0
    items = []
    notes = []
    feasible = True

    for r in rows:
        po = r["po_id"]
        w = float(r["weight_tonnes"])

        # if item itself > capacity, still place it (solo) and mark infeasible
        if w > capacity_t_per_week:
            notes.append(f"{po}: weight {w}t exceeds weekly capacity {capacity_t_per_week}t (cannot fit).")
            feasible = False

        # move to next week if adding this would exceed remaining capacity
        if used > 0 and used + w > capacity_t_per_week:
            cur_year, cur_week = advance_week(cur_year, cur_week)
            used = 0.0

        # place item in current week
        start_w = end_w = f"{cur_year:04d}-W{cur_week:02d}"
        used += w

        # deadline check
        y_due, w_due, _ = date.fromisoformat(r["due_date"]).isocalendar()
        if not week_leq(cur_year, cur_week, y_due, w_due):
            feasible = False
            notes.append(f"{po}: scheduled in {end_w} but due week is {y_due:04d}-W{w_due:02d}.")

        items.append({
            "po_id": po,
            "weight_tonnes": w,
            "due_date": r["due_date"],
            "start_week": start_w,
            "end_week": end_w
        })

        # if we exactly hit capacity, advance for the next item
        if abs(used - capacity_t_per_week) < 1e-9:
            cur_year, cur_week = advance_week(cur_year, cur_week)
            used = 0.0

    return {
        "items": items,
        "feasible": feasible,
        "notes": notes
    }
