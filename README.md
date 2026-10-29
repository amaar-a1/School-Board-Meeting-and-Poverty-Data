# School Board Meetings & Poverty Data Prototype App

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
- The **Urban & suburban districts only** section appears when the spreadsheet has a column named `Locale` (or `Urban`, `Urban District`, `Urbanicity`, `Urban/Rural`). A district is included if that cell says `Urban` or `Suburban` (also `Yes`, `True`, `1`, `X`, or an NCES "City"/"Suburb" locale). `Town`, `Rural` or a blank cell are left out. An **Urban districts only** section does the same for `Urban` (NCES "City") districts alone, without suburbs.
- [`data-prep/district_locales.csv`](data-prep/district_locales.csv) lists each district's locale with the NCES record it was matched to (NCES Common Core of Data 2023, via the Urban Institute Education Data API). NCES locale codes 11–13 are City (Urban), 21–23 Suburb (Suburban), 31–33 Town, 41–43 Rural.
- The **By district size** tab groups districts by NCES student enrollment (2023): Low 0–499, Medium 500–9,999, Big 10,000–49,999, Large 50,000–99,999, Huge 100,000+. For each tier it compares child poverty for districts with vs. without available meetings, the share of districts with meetings, average meetings, meetings per 10,000 students and meetings per poverty point. It also checks the 10,000-student rule (Texas Government Code § 551.128). Enrollment comes from an `Enrollment` column in the sheet; if the sheet has none, the workflow adds NCES enrollment from `data-prep/district_locales.csv` when it downloads the data. `data-prep/enrollment_column_for_sheet.txt` is that column in sheet row order, ready to paste.
- **United States / state menu:** a button and a menu at the top switch every view between the national data and any single state or DC. Each state's view is the national rows for that state; Texas uses the project spreadsheet. On the By district size tab, each state shows its rules from `docs/state-rules.js`, and states with an enrollment cutoff (Texas, Oregon) get a count of the districts it covers.
- **Texas / United States data:** every view can switch between the Texas data (`docs/data/data.csv`, from the spreadsheet) and nationwide data (`docs/data/national.csv`). The national file has every school district in the Census SAIPE 2024 file (13,132, Texas included), with NCES 2023 enrollment and locale and the meeting count from CivicSearch's district list (1,206 districts; the rest are 0). For Texas it matches the spreadsheet exactly. It is a snapshot (October 29, 2026). To rebuild it, download the three inputs listed at the top of `data-prep/build_national.py` and run that script. `data-prep/civicsearch_matches.csv` shows which district each CivicSearch entry was matched to.
- Only the first tab is exported. To change the spreadsheet, edit `SHEET_ID` in the workflow.
- In the repo, go to **Settings → Pages** and set **Source** to **GitHub Actions** (if the first deploy didn't enable it automatically).

### Run locally

```sh
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```
