// Site settings. The CSV files in docs/data/ are downloaded from the project
// spreadsheet by .github/workflows/pages.yml.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // CSV files to load. "United States" gets a button; each state is picked from a menu
  // (see perState). Texas uses the project spreadsheet; other states come from the national file.
  dataFiles: [
    { name: "Texas", file: "data/data.csv", state: "TX",
      note: "1,017 Texas school districts.",
      footer: "Poverty figures are for children ages 5–17. Data is refreshed daily. Sources are listed on the Sources tab." },
    { name: "United States", file: "data/national.csv", textColumns: ["District ID"],
      // {rows} and {withMeetings} are filled in from the data when the page loads.
      note: "{rows} school districts in the 50 states and DC. Meeting counts are available for {withMeetings} of them; the rest show 0.",
      footer: "Poverty figures are for children ages 5–17. Meeting counts are refreshed daily from CivicSearch. Sources are listed on the Sources tab." },
    // The territories share one menu entry (see perState.after). They have no meeting
    // counts or school-district poverty figures, so this view only lists their school systems.
    { name: "U.S. territories", file: "data/territories.csv", state: "territories",
      chart: { type: "bar", x: "District", y: "Enrollment" },
      note: "Puerto Rico, Guam, the Northern Mariana Islands, the U.S. Virgin Islands and American Samoa, shown together. Each runs one territory-wide school system (the Virgin Islands has two districts under one board). Meeting counts aren't available for the territories, and the Census has child poverty figures only for Puerto Rico, so this view lists each school system and whether its board posts meetings online. The online-meetings column is reported, not yet checked against official sites. Enrollment is from the NCES 2023 directory, which has no figure for Guam or American Samoa; Guam's four charter schools, listed separately by NCES, are left out.",
      footer: "Territory school systems as of October 30, 2026. Sources are listed on the Sources tab." }
  ],
  // State menu: every state and DC. Each state's view is the national rows with this
  // State value (Texas uses its own data set above).
  perState: {
    from: "United States",
    column: "State",
    names: {
      AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California", CO: "Colorado", CT: "Connecticut",
      DE: "Delaware", DC: "District of Columbia", FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois",
      IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana", ME: "Maine", MD: "Maryland",
      MA: "Massachusetts", MI: "Michigan", MN: "Minnesota", MS: "Mississippi", MO: "Missouri", MT: "Montana",
      NE: "Nebraska", NV: "Nevada", NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York",
      NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon", PA: "Pennsylvania",
      RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota", TN: "Tennessee", TX: "Texas", UT: "Utah",
      VT: "Vermont", VA: "Virginia", WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming"
    },
    // Listed after the states, in this order.
    after: { territories: "U.S. territories" }
  },
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
    ]
  },
  sourcesUrl: "https://docs.google.com/document/d/1U5bDB31MpETIwG8Q8xZ7MZdH9oNooY_W6TnpSkNdBFk/edit?usp=drivesdk"
};
