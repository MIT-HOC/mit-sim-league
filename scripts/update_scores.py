"""Copy new rounds from the score form's Google Sheet into site/data/scores.json.

Run every hour by .github/workflows/update.yml. Only three columns are kept:
Timestamp, Team name and the score, exactly as typed. Emails, photo links and
every other column are dropped and never written to the repository.

The sheet link is read from the SHEET_CSV_URL secret so it never appears in this
public repo. It should look like:
https://docs.google.com/spreadsheets/d/<sheet id>/export?format=csv
"""
import csv
import io
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

OUT = "site/data/scores.json"


def column(headers, *keywords):
    """Index of the first header containing one of the keywords (checked in order)."""
    lowered = [h.strip().lower() for h in headers]
    for kw in keywords:
        for i, h in enumerate(lowered):
            if kw in h:
                return i
    sys.exit(f"Couldn't find a column for {keywords} in the sheet headers: {headers}")


url = os.environ.get("SHEET_CSV_URL", "").strip()
if not url:
    sys.exit("The SHEET_CSV_URL secret isn't set. Add it under Settings → Secrets and variables → Actions.")

req = urllib.request.Request(url, headers={"User-Agent": "mit-sim-league-updater"})
text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8-sig")
if text.lstrip().startswith("<"):
    sys.exit("Google returned a web page instead of CSV. Check the sheet is shared as "
             "'Anyone with the link can view' and the link ends in export?format=csv")

rows = list(csv.reader(io.StringIO(text)))
if not rows:
    sys.exit("The sheet came back empty.")
headers = rows[0]
ts = column(headers, "timestamp")
team = column(headers, "team")
score = column(headers, "shoot", "gross", "score")

scores = []
for r in rows[1:]:
    if len(r) <= max(ts, team, score) or not r[ts].strip():
        continue
    scores.append({"at": r[ts].strip(), "team": r[team].strip(), "score": r[score].strip()})

try:
    old = json.load(open(OUT, encoding="utf-8"))
except FileNotFoundError:
    old = {"rows": []}

if scores == old.get("rows"):
    print(f"No change ({len(scores)} rounds).")
    sys.exit(0)

if len(scores) < len(old.get("rows", [])):
    print(f"Note: the sheet now has {len(scores)} rounds, fewer than the {len(old['rows'])} saved before "
          "(a response was deleted). Mirroring the sheet.")

eastern = timezone(timedelta(hours=-5 if datetime.now(timezone.utc).month in (11, 12, 1, 2) else -4))
json.dump({"updated": datetime.now(eastern).isoformat(timespec="minutes"), "rows": scores},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Saved {len(scores)} rounds ({len(scores) - len(old.get('rows', []))} new).")
