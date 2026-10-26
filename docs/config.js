// Site settings. The CSV files in docs/data/ are downloaded from the project
// spreadsheet by .github/workflows/pages.yml.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // CSV files to show. Each one gets its own tab on the page when there is more than one.
  dataFiles: [
    { name: "Data", file: "data/data.csv" }
  ],
  sourcesUrl: "https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk"
};
