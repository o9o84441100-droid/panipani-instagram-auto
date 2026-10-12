"""Detect unrecorded daily Reel slots; never retry public posting blindly."""
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
SLOTS = ("0800", "1000", "1200", "1800", "2100")
PROJECT_STARTED = date(2026, 10, 13)


def audit(reference=None, root=Path("state/posts")):
    check_day = reference or (datetime.now(JST).date() - timedelta(days=1))
    if check_day < PROJECT_STARTED:
        return check_day, []
    missing = [slot for slot in SLOTS
               if not (root / f"{check_day.isoformat()}_{slot}.json").exists()]
    return check_day, missing


def main():
    day, missing = audit()
    print("Auditing date:", day.isoformat(), file=sys.stderr)
    print("Missing ledger slots:", ", ".join(missing) or "(none)", file=sys.stderr)
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as out:
            out.write("date=" + str(day) + "\n")
            out.write("missing_count=" + str(len(missing)) + "\n")
            out.write("missing_slots=" + ",".join(missing) + "\n")
    report_dir = Path("output")
    report_dir.mkdir(exist_ok=True)
    report = [
        f"## Panipani daily publishing ledger alert: {day.isoformat()}",
        "",
        "The following expected Japan-time posting slots have **no verified ledger entry**:",
        "",
        *["- " + time[:2] + ":" + time[2:] + " JST" for time in missing],
        "",
        "**Unrecorded is not definitive proof of unpublished.** The Instagram API may have",
        "accepted the media even if the later GitHub ledger commit failed.",
        "",
        "Before any retry, inspect Instagram account @reiv2220 and the GitHub Actions",
        "runs (including the Published media ID and Verified Instagram media log lines).",
        "Never blindly retry a publish step as it could create duplicates.",
        "",
        "GitHub Actions: https://github.com/o9o84441100-droid/panipani-instagram-auto/actions",
        "Posted ledger: https://github.com/o9o84441100-droid/panipani-instagram-auto/tree/main/state/posts",
    ]
    (report_dir / "missing_report.md").write_text("\n".join(report) + "\n",
                                                   encoding="utf-8")
    if missing:
        print("Review required: expected Reel ledger records absent.", file=sys.stderr)


if __name__ == "__main__":
    main()
