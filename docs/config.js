// Where the site gets its data. Edit these values to point at a different sheet.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // Google Sheet ID (the long string in the sheet's URL). The sheet must be
  // shared as "Anyone with the link can view".
  sheetId: "1xuFUnNHIjKzbwQ-qSMAIGNy5PjzjW2g5tKZHKUWSysc",
  // Tab names to load. Leave empty to load only the first tab.
  // Example: ["Meetings", "Poverty"]
  sheets: [],
  // Used if the live sheet can't be reached (e.g. offline). Export the sheet
  // as CSV and save it to docs/data/data.csv to enable this.
  fallbackCsv: "data/data.csv",
  sourcesUrl: "https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk",
  spreadsheetUrl: "https://docs.google.com/spreadsheets/d/1xuFUnNHIjKzbwQ-qSMAIGNy5PjzjW2g5tKZHKUWSysc/edit?usp=drivesdk"
};
