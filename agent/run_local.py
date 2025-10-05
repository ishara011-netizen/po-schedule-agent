# agent/run_local.py
import re, json, sys
from pathlib import Path

# Ensure we can import from the project root (so "tools" works)
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from tools.parsers import read_po_csv
from tools.schedule import schedule_cap_120t_week
from tools.checks import risk_checks

EMAIL_PATH = Path("data/emails/req1.txt")

def parse_email_req(path: Path):
    text = path.read_text(encoding="utf-8")

    job = None
    m = re.search(r'project\s+"([^"]+)"', text, flags=re.I)
    if m:
        job = m.group(1).strip()
    if not job:
        m = re.search(r"Subject:\s*(.+)", text)
        if m:
            job = m.group(1).strip()

    m = re.search(r"CSV path:\s*(.+)", text, flags=re.I)
    csv_path = m.group(1).strip() if m else None

    m = re.search(r"Start week:\s*([0-9]{4}-W[0-9]{2})", text, flags=re.I)
    start_week = m.group(1).strip() if m else None

    if not (job and csv_path and start_week):
        raise ValueError("Email missing job, CSV path, or start week.")

    return {"job": job, "csv_path": csv_path, "start_week": start_week}

def main():
    req = parse_email_req(EMAIL_PATH)
    rows = read_po_csv(req["csv_path"])
    plan_items = schedule_cap_120t_week(rows, req["start_week"])
    check = risk_checks(plan_items)

    out = {
        "job": req["job"],
        "items": plan_items,
        "feasible": check["feasible"],
        "notes": check["notes"],
    }

    Path("schedule.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote schedule.json with", len(plan_items), "items. Feasible:", check["feasible"])

if __name__ == "__main__":
    main()
