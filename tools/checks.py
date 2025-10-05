from datetime import date
from typing import List, Dict, Tuple
from collections import defaultdict

CAP = 120.0  # tonnes/week

def _parse_week(week_str: str) -> Tuple[int, int]:
    # "YYYY-Www" -> (YYYY, ww)
    try:
        y = int(week_str[:4])
        w = int(week_str[6:])
        return y, w
    except Exception:
        raise ValueError(f"Bad ISO week format: {week_str!r}. Expected YYYY-Www (e.g., 2025-W40).")

def _week_tuple_from_date_str(d: str) -> Tuple[int, int]:
    # "YYYY-MM-DD" -> (YYYY, ww)
    y, w, _ = date.fromisoformat(d).isocalendar()
    return int(y), int(w)

def risk_checks(plan_items: List[Dict]) -> Dict:
    """
    Validate the planned items:
    - any item scheduled after its due_date week -> note + infeasible
    - any ISO week totals > CAP -> note + infeasible
    Returns: {"feasible": bool, "notes": [str, ...]}
    """
    notes: List[str] = []
    feasible = True

    # 1) due-date checks
    for it in plan_items:
        due_yw = _week_tuple_from_date_str(it["due_date"])
        end_yw = _parse_week(it["end_week"])
        if end_yw > due_yw:
            feasible = False
            notes.append(
                f"{it['po_id']} misses due week (due {due_yw[0]}-W{due_yw[1]:02d}, planned {it['end_week']})."
            )
        if float(it["weight_tonnes"]) < 0:
            feasible = False
            notes.append(f"{it['po_id']} has negative weight_tonnes.")

    # 2) capacity checks (sum per week must be <= CAP)
    by_week = defaultdict(float)
    for it in plan_items:
        by_week[it["start_week"]] += float(it["weight_tonnes"])
    for wk, total in by_week.items():
        if total > CAP + 1e-9:
            feasible = False
            notes.append(f"Week {wk} exceeds capacity: {total:.1f}t > {CAP:.1f}t.")

    return {"feasible": feasible, "notes": notes or ["ok"]}
