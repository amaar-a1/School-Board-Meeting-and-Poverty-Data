// Site settings. docs/data/national.csv is rebuilt daily by .github/workflows/pages.yml
// with fresh CivicSearch meeting counts.
window.SITE_CONFIG = {
  title: "School Board Meetings & Poverty Data",
  // CSV files to load. "United States" gets a button; each state is picked from a menu
  // (see perState) and comes from the national file.
  dataFiles: [
    { name: "United States", file: "data/national.csv", textColumns: ["District ID"],
      // {rows} and {withMeetings} are filled in from the data when the page loads.
      note: "{rows} school districts in the 50 states and DC. Meeting counts are available for {withMeetings} of them; the rest show 0.",
      footer: "Poverty figures are for children ages 5–17. Meeting counts are refreshed daily from CivicSearch. Sources are listed on the Sources tab." },
    // The territories share one menu entry (see perState.after). They have no meeting
    // counts or school-district poverty figures, so this view only lists their school systems.
    { name: "U.S. territories", file: "data/territories.csv", state: "territories", textColumns: ["District ID"],
      chart: { type: "bar", x: "District", y: "Percentage of Children Ages 5-17 in Poverty" },
      rulesNote: "The territories' rules on recording or streaming board meetings haven't been researched yet.",
      note: "Puerto Rico, Guam, the Northern Mariana Islands, the U.S. Virgin Islands and American Samoa, shown together. Each runs one territory-wide school system (the Virgin Islands has two districts under one board). CivicSearch doesn't cover the territories, so their meeting counts are the board meetings recorded on the boards' own YouTube channels (checked October 30, 2026; a meeting split across several videos counts once): Guam has 21 (October 2025 to October 2026) and the Northern Mariana Islands 6 (May to October 2026; its board meets on Zoom and its website posts no recordings); the Virgin Islands board posts only agendas and minutes, American Samoa had none, and Puerto Rico has no board. Recordings posted only on Facebook couldn't be checked. These counts aren't directly comparable with CivicSearch's. Puerto Rico's poverty figures are Census estimates for 2024; the other territories' come from the 2020 Census (2019 income) and count children living in households (on Guam, not counting military housing), so they aren't directly comparable with Puerto Rico's or the states'. The Virgin Islands figures are split by island to match its two districts. Enrollment and locale are from the NCES directory: 2023, except Guam (2021) and American Samoa (2020), the latest years NCES has enrollment for them; Guam's four charter schools, listed separately by NCES, are left out.",
      footer: "Territory school systems as of October 30, 2026. Sources are listed on the Sources tab." }
  ],
  // State menu: every state and DC. Each state's view is the national rows with this
  // State value.
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
