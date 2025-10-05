import csv
from typing import List, Dict

def read_po_csv(path: str) -> List[Dict]:
    """
    Read a Purchase Order CSV with columns:
    po_id,weight_tonnes,due_date (YYYY-MM-DD)
    Returns a list of dicts with normalized types.
    """
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader, start=1):
            po_id = (r.get("po_id") or "").strip()
            wt = r.get("weight_tonnes")
            due = (r.get("due_date") or "").strip()
            try:
                weight = float(wt)
            except (TypeError, ValueError):
                raise ValueError(f"Row {i}: invalid weight_tonnes={wt!r}")
            rows.append({"po_id": po_id, "weight_tonnes": weight, "due_date": due})
    if not rows:
        raise ValueError("CSV has no data rows.")
    return rows
