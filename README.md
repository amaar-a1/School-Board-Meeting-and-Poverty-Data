# School Board Meetings & Poverty Data

A website that shows the project's school board meeting and poverty data with summary stats, an interactive chart, and a searchable, sortable table you can download.

- **Data:** [project spreadsheet](https://docs.google.com/spreadsheets/d/1xuFUnNHIjKzbwQ-qSMAIGNy5PjzjW2g5tKZHKUWSysc/edit?usp=drivesdk). The site reads it live, so edits to the sheet show up automatically.
- **Sources:** [sources document](https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk)

## How it works

The site is a static page in `docs/`, deployed to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`.

| File | Purpose |
| --- | --- |
| `docs/config.js` | Spreadsheet ID, which tabs to load, links |
| `docs/sources.js` | Sources listed on the page |
| `docs/data/data.csv` | Optional saved copy of the data, used if the live sheet can't be reached |
| `docs/app.js`, `docs/style.css`, `docs/index.html` | The site itself |

### Requirements

- The spreadsheet must be shared as **Anyone with the link → Viewer**.
- To show more than the first tab, list the tab names in `sheets` in `docs/config.js`.
- In the repo, go to **Settings → Pages** and set **Source** to **GitHub Actions** (if the first deploy didn't enable it automatically).

### Run locally

```sh
cd docs && python3 -m http.server 8000
# open http://localhost:8000
```
