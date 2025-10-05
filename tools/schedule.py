from datetime import date, timedelta
from typing import List, Dict, Tuple

CAP = 120.0  # tonnes per week

def _parse_week(week_str: str) -> Tuple[int, int]:
    # "YYYY-Www" -> (YYYY, ww)
    try:
        y = int(week_str[:4])
        w = int(week_str[6:])
        return y, w
    except Exception:
        raise ValueError(f"Bad ISO week format: {week_str!r}. Expected YYYY-Www (e.g., 2025-W40).")

def _week_to_str(y: int, w: int) -> str:
    return f"{y}-W{w:02d}"

def _next_week(week_str: str) -> str:
    y, w = _parse_week(week_str)
    # Monday of this ISO week, then add 7 days and re-read the ISO week
    monday = date.fromisocalendar(y, w, 1)
    nxt = monday + timedelta(days=7)
    y2, w2, _ = nxt.isocalendar()
    return _week_to_str(y2, w2)

def schedule_cap_120t_week(rows: List[Dict], start_week: str) -> List[Dict]:
    """
    Greedy packer: place items into ISO weeks so total per week <= 120 t.
    Sorts by due_date first (earliest due first).
    Returns a list of items with start_week/end_week filled.
    """
    # sort by due_date so nearer deadlines go earlier
    rows_sorted = sorted(rows, key=lambda r: (r.get("due_date", ""), r.get("po_id", "")))

    week = start_week
    used_this_week = 0.0
    plan_items: List[Dict] = []

    for r in rows_sorted:
        wt = float(r["weight_tonnes"])

        # if adding this item would exceed capacity and we already packed some this week,
        # move to the next week before placing it.
        if used_this_week > 0.0 and used_this_week + wt > CAP:
            week = _next_week(week)
            used_this_week = 0.0

        plan_items.append({
            "po_id": r["po_id"],
            "weight_tonnes": wt,
            "due_date": r["due_date"],
            "start_week": week,
            "end_week": week
        })

        used_this_week += wt

        # exactly full? advance to next week for the next item
        if used_this_week >= CAP - 1e-9:
            week = _next_week(week)
            used_this_week = 0.0

    return plan_items
