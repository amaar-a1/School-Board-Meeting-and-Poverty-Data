// Site settings. The CSV files in docs/data/ are downloaded from the project
// spreadsheet by .github/workflows/pages.yml.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // CSV files to show. Each one gets its own tab on the page when there is more than one.
  dataFiles: [
    { name: "Data", file: "data/data.csv" }
  ],
  recordLabel: "Districts",
  // Chart shown when the page opens (the viewer can change it).
  chart: {
    type: "scatter",
    x: "Percentage of Children Ages 5-17 in Poverty",
    y: "Available Board Meetings"
  },
  // Compares districts with vs. without available board meetings.
  compare: {
    title: "Child poverty: districts with vs. without available board meetings",
    by: "Available Board Meetings",
    metric: "Percentage of Children Ages 5-17 in Poverty",
    withLabel: "With 1+ available meetings",
    withoutLabel: "With no available meetings"
  },
  // "Urban districts only" section. It appears when the data has one of these
  // columns. A district counts as urban if the cell says Yes/True/1/X/Urban,
  // or is an NCES locale starting with "City" (e.g. "City: Large").
  urban: {
    columns: ["Urban", "Urban District", "Locale", "Urbanicity", "Urban/Rural"]
  },
  sourcesUrl: "https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk"
};
