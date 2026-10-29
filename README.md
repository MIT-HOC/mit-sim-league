# MIT Sim League

League table, handicap calculator and playoff bracket for the MIT Golf Club Fall 2026 simulator league.

## How it updates

- **Scores:** every hour a GitHub Action (`.github/workflows/update.yml`) reads the score form's Google Sheet and copies the Timestamp, Team name and score into `site/data/scores.json`. Nothing else from the sheet is saved. The sheet link is kept in the `SHEET_CSV_URL` secret, not in this repo.
- **Fixing a score:** edit or delete the response in the Google Sheet. The site mirrors the sheet at the next hourly run.
- **Teams and handicaps:** `site/data/teams.json` holds team names, players and team handicaps (no individual handicaps). Replace that file to change teams; the site republishes within a couple of minutes.
- **Team name typos on the form:** add them to `"aliases"` in `teams.json`, e.g. `"La Raza": "Spanish Latinos"`.
- **Run it now:** Actions tab → "Update scores and publish site" → Run workflow.

## Files

- `site/index.html` — the page
- `site/data/teams.json` — teams, team handicaps, allowance table
- `site/data/scores.json` — rounds copied from the form (written by the Action)
- `scripts/update_scores.py` — the hourly copy step
