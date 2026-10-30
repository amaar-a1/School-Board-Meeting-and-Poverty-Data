# School Board Meetings & Poverty Data Prototype App

A website that shows the project's school board meeting and poverty data with summary stats, an interactive chart, and a searchable, sortable table you can download.

- **Data:** [`docs/data/national.csv`](docs/data/national.csv), every school district in the 50 states and DC, with meeting counts refreshed daily from CivicSearch. [`docs/data/territories.csv`](docs/data/territories.csv) covers the U.S. territories.
- **Sources:** [sources document](https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk)

## How it works

The site is a static page in `docs/` that reads its data from CSV files in `docs/data/`. The workflow `.github/workflows/pages.yml` downloads CivicSearch's district list, rebuilds `docs/data/national.csv` with `data-prep/build_national.py`, commits it if it changed, and deploys the site to GitHub Pages. It runs on every push to `main`, once a day, and on demand (**Actions → Update data and deploy website → Run workflow**).

| File | Purpose |
| --- | --- |
| `docs/config.js` | Which CSV files to show, links |
| `docs/sources.js` | Sources listed on the page |
| `docs/state-rules.js` | State rules on recording or streaming meetings |
| `docs/data/national.csv` | US data shown on the site (meeting counts refreshed daily) |
| `docs/data/territories.csv` | U.S. territories data |
| `docs/data/data.csv` | The project spreadsheet's Texas data as of October 29, 2026 (kept for reference; the site no longer uses it) |
| `docs/app.js`, `docs/style.css`, `docs/index.html` | The site itself |

### Details

- **National data:** `national.csv` has every school district in the 50 states and DC from the Census SAIPE 2024 file (13,131; Puerto Rico, the file's only territory, is in the territories view instead), with NCES 2023 enrollment and locale and the meeting count from CivicSearch's district list (the rest show 0). The workflow reruns `data-prep/build_national.py` daily with a fresh CivicSearch list and the Census and NCES files saved in `data-prep/inputs/` (the NCES file is trimmed to the fields the script uses). If the download fails or looks wrong, the site keeps the last good data. `data-prep/civicsearch_matches.csv` shows which district each CivicSearch entry was matched to.
- **Texas:** the Texas view is the national rows for Texas, like every other state. On October 29, 2026 these matched the project spreadsheet's numbers for all 1,017 districts (the names use the Census's full form, e.g. "Austin Independent School District"). The spreadsheet is no longer downloaded; its last copy is `docs/data/data.csv`.
- **United States / state menu:** a button and a menu at the top switch every view between the national data and any single state or DC. On the By district size tab, each state shows its rules from `docs/state-rules.js`, and states with an enrollment cutoff (Texas, Oregon) get a count of the districts it covers. The last menu entry, U.S. territories, shows Puerto Rico, Guam, the Northern Mariana Islands, the U.S. Virgin Islands and American Samoa together from `docs/data/territories.csv`. That file lists each territory's school system, its board and whether the board posts meetings online, with NCES 2023 schools and enrollment, and the Census child poverty figures for Puerto Rico. The territories have no meeting counts, so that view has no comparison or size tab. Its sources show only on its own Sources tab, and the state rules sources show only for the states.
- **Urban sections:** the **Urban & suburban districts only** section uses the `Locale` column (or `Urban`, `Urban District`, `Urbanicity`, `Urban/Rural`). A district is included if that cell says `Urban` or `Suburban` (also `Yes`, `True`, `1`, `X`, or an NCES "City"/"Suburb" locale). `Town`, `Rural` or a blank cell are left out. An **Urban districts only** section does the same for `Urban` (NCES "City") districts alone, without suburbs. NCES locale codes 11–13 are City (Urban), 21–23 Suburb (Suburban), 31–33 Town, 41–43 Rural.
- **By district size** groups districts by NCES student enrollment (2023): Low 0–499, Medium 500–9,999, Big 10,000–49,999, Large 50,000–99,999, Huge 100,000+. For each tier it compares child poverty for districts with vs. without available meetings, the share of districts with meetings, average meetings, meetings per 10,000 students and meetings per poverty point.
- Earlier spreadsheet helpers are kept in `data-prep/`: `district_locales.csv` (each spreadsheet district's NCES match, locale and enrollment) and the `*_column_for_sheet.txt` files.
- In the repo, go to **Settings → Pages** and set **Source** to **GitHub Actions** (if the first deploy didn't enable it automatically).

### Run locally

```sh
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```
