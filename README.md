# School Board Meetings & Poverty Data

A website that shows the project's school board meeting and poverty data with summary stats, an interactive chart, and a searchable, sortable table you can download.

- **Data:** [`docs/data/data.csv`](docs/data/data.csv), exported from the [project spreadsheet](https://docs.google.com/spreadsheets/d/1qphCSWlKrBUIsodbmafpjaW75Jg-h8fgdxqlyJ_jys0/edit?usp=drivesdk).
- **Sources:** [sources document](https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk)

## How it works

The site is a static page in `docs/` that reads its data from CSV files in `docs/data/`. The workflow `.github/workflows/pages.yml` downloads the spreadsheet as `docs/data/data.csv`, commits it if it changed, and deploys the site to GitHub Pages. It runs on every push to `main`, once a day, and on demand (**Actions → Update data and deploy website → Run workflow**).

| File | Purpose |
| --- | --- |
| `docs/config.js` | Which CSV files to show, links |
| `docs/sources.js` | Sources listed on the page |
| `docs/data/data.csv` | The data shown on the site (auto-updated from the spreadsheet) |
| `docs/app.js`, `docs/style.css`, `docs/index.html` | The site itself |

### Requirements

- The spreadsheet must be shared as **Anyone with the link → Viewer** so the workflow can download it.
- The **Urban districts only** section appears when the spreadsheet has a column named `Urban` (or `Urban District`, `Locale`, `Urbanicity`, `Urban/Rural`). A district counts as urban if that cell says `Yes`, `True`, `1`, `X` or `Urban`, or is an NCES locale starting with "City" (for example `City: Large`). Any other value, or a blank cell, counts as not urban.
- Only the first tab is exported. To change the spreadsheet, edit `SHEET_ID` in the workflow.
- In the repo, go to **Settings → Pages** and set **Source** to **GitHub Actions** (if the first deploy didn't enable it automatically).

### Run locally

```sh
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```
