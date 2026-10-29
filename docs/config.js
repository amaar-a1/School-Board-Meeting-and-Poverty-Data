// Site settings. The CSV files in docs/data/ are downloaded from the project
// spreadsheet by .github/workflows/pages.yml.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // CSV files to show. Each one gets its own tab on the page when there is more than one.
  dataFiles: [
    { name: "Texas", file: "data/data.csv",
      note: "1,017 Texas school districts, from the project spreadsheet.",
      footer: "Poverty figures are for children ages 5–17. Data is refreshed from the project spreadsheet daily." },
    // law: "none" hides the 10,000-student rule card on the "By district size" tab.
    { name: "United States", file: "data/national.csv", textColumns: ["NCES LEAID"], law: "none",
      note: "All 13,132 US school districts in the Census SAIPE 2024 file. Meeting counts are from CivicSearch's district list (October 29, 2026), which covers 1,206 of these districts; the rest show 0.",
      footer: "Poverty figures are for children ages 5–17. This data is a snapshot from October 29, 2026." }
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
  // "Urban & suburban districts only" and "Urban districts only" sections. They
  // appear when the data has one of these columns. The first counts cells saying
  // Urban/Suburban/Yes/True/1/X or an NCES "City"/"Suburb" locale; the second
  // counts only Urban or an NCES "City" locale (e.g. "City: Large").
  urban: {
    columns: ["Urban", "Urban District", "Locale", "Urbanicity", "Urban/Rural"]
  },
  // "By district size" tab. Districts are grouped by NCES student enrollment.
  sizeTiers: {
    column: "Enrollment",
    tiers: [
      { name: "Low", min: 0, max: 499 },
      { name: "Medium", min: 500, max: 9999 },
      { name: "Big", min: 10000, max: 49999 },
      { name: "Large", min: 50000, max: 99999 },
      { name: "Huge", min: 100000 }
    ],
    // Texas Government Code § 551.128: districts with 10,000+ students must make
    // their board meetings available online.
    lawThreshold: 10000,
    lawUrl: "https://codes.findlaw.com/tx/government-code/gov-t-sect-551-128/"
  },
  sourcesUrl: "https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk"
};
