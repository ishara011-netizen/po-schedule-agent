# agent/run_local.py
# Local runner: reads the sample email/CSV values (hardcoded for now),
# builds the schedule, and writes schedule.json that matches schemas/schedule.schema.json.

import json
from pathlib import Path
from tools.schedule import read_po_csv, schedule_rows

JOB = "Waterdown"
CSV_PATH = Path("data/po_csv/sample.csv")
START_WEEK = "2025-W40"       # from your email
CAPACITY = 120.0              # tonnes/week

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")

    rows = read_po_csv(str(CSV_PATH))
    plan = schedule_rows(rows, START_WEEK, capacity_t_per_week=CAPACITY)

    # shape to match the schema
    out = {
        "job": JOB,
        "items": plan["items"],
        "feasible": plan["feasible"],
        "notes": plan["notes"]
    }

    out_path = Path("schedule.json")
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(plan['items'])} items). Feasible={plan['feasible']}")
    if plan["notes"]:
        print("Notes:")
        for n in plan["notes"]:
            print(" -", n)

if __name__ == "__main__":
    main()
