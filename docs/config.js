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
      note: "Puerto Rico, Guam, the Northern Mariana Islands, the U.S. Virgin Islands and American Samoa, shown together. Each runs one territory-wide school system (the Virgin Islands has two districts under one board). CivicSearch doesn't cover the territories, so their meeting counts are the board meetings recorded on the boards' own YouTube channels (checked October 30, 2026; a meeting split across several videos counts once): Guam has 21 (October 2025 to October 2026) and the Northern Mariana Islands 6 (May to October 2026; its board meets on Zoom and its website posts no recordings); the Virgin Islands board posts only agendas and minutes, American Samoa had none, and Puerto Rico has no board, so its count is the Legislature's education committee sessions (21) instead. Recordings posted only on Facebook couldn't be checked. These counts aren't directly comparable with CivicSearch's. Puerto Rico's poverty figures are Census estimates for 2024; the other territories' come from the 2020 Census (2019 income) and count children living in households (on Guam, not counting military housing), so they aren't directly comparable with Puerto Rico's or the states'. The Virgin Islands figures are split by island to match its two districts. Enrollment and locale are from the NCES directory: 2023, except Guam (2021) and American Samoa (2020), the latest years NCES has enrollment for them; Guam's four charter schools, listed separately by NCES, are left out.",
      footer: "Territory school systems as of October 30, 2026. Sources are listed on the Sources tab." },
    // Canada: its own button and its own provinces in the menu. Kept apart from the US figures,
    // because its low-income measure (ages 0-17, LIM-AT) isn't the same as the US one (ages 5-17, SAIPE).
    { name: "Canada", file: "data/canada.csv", country: "CA", recordLabel: "Boards",
      groups: { column: "Province", label: "Canada",
        names: { AB: "Alberta", BC: "British Columbia", MB: "Manitoba", NB: "New Brunswick", NL: "Newfoundland and Labrador",
          NS: "Nova Scotia", NT: "Northwest Territories", NU: "Nunavut", ON: "Ontario", PE: "Prince Edward Island", QC: "Quebec",
          SK: "Saskatchewan", YT: "Yukon" } },
      chart: { type: "scatter", x: "Percentage of Children Ages 0-17 in Low Income", y: "Available Board Meetings" },
      compare: {
        title: "Child low income: boards with vs. without board meetings found",
        by: "Available Board Meetings",
        metric: "Percentage of Children Ages 0-17 in Low Income",
        withLabel: "With 1+ meetings found",
        withoutLabel: "With no meetings found"
      },
      textColumns: ["District ID", "Enrollment year"],
      sizeNote: "Canada's data has no enrollment figures, so boards can't be grouped by size.",
      sizeYearNote: "Boards are grouped by student enrollment from each province's latest published figures (see the “Enrollment year” column: mostly 2024–25 or 2025–26; Quebec September 2022; Saskatchewan September 30, 2024). A few boards' figures come from other sources and are noted in the “Enrollment note” column (the Northwest Territories' are full-time-equivalent grades 1–12). PEI's French board and the Yukon First Nation School Board have no figure yet.",
      note: "{rows} Canadian school boards and school service centres in every province and territory. Canada has no site like CivicSearch, so meeting counts are the board meetings each board has posted on its own YouTube channel (meetings found for {withMeetings} boards; the rest show 0, which can also mean the board streams elsewhere). Low income is Statistics Canada's after-tax low-income measure (LIM-AT) for children ages 0–17 from the 2021 Census (2020 incomes), worked out for each board from the census subdivisions inside its border; see the “How poverty was calculated” column. These figures aren't comparable with the US child poverty rates. Enrollment comes from each province's latest published figures, with a few from other sources (see the “Enrollment note” column); none yet for PEI's French board or the Yukon First Nation School Board.",
      footer: "Canadian boards, borders and low-income figures as built in November 2026. Sources are listed on the Sources tab." },
    // Saint-Pierre-et-Miquelon (France): its own button. No elected school board, no child poverty figure.
    { name: "Saint-Pierre-et-Miquelon (France)", button: "Saint-Pierre-et-Miquelon", file: "data/spm.csv", country: "FR",
      recordLabel: "School systems", textColumns: ["District ID", "Enrollment year"],
      sizeYearNote: "Grouped by student enrollment at the start of the 2024 school year (France's Ministry of Education).",
      localeNote: "Saint-Pierre-et-Miquelon is counted as a town (its main town, Saint-Pierre, has about 5,500 people); this isn't an NCES locale.",
      compare: { title: "Unemployment (stand-in for poverty): with vs. without meetings", by: "Available Board Meetings",
        metric: "Unemployment rate (stand-in for poverty)", withLabel: "With 1+ meetings", withoutLabel: "With no meetings" },
      note: "Saint-Pierre-et-Miquelon, a French overseas collectivity next to Newfoundland. It has no elected school board: its schools are run by the French state's education office (Service de l'Éducation nationale), which reports to the Académie de Normandie and holds no public meetings. As a stand-in, like Puerto Rico's, the meeting count is the official sessions of the elected Territorial Council (Conseil territorial): at least 12 from January 2025 to October 2026, found from the dates on the deliberations it publishes in its official gazette; these are written records, not recordings, so they aren't comparable with CivicSearch's counts. Enrollment is from France's Ministry of Education (start of the 2024 school year, public and private schools under contract). No child poverty rate is published for the archipelago, so its unemployment rate stands in: 8.7% (2015 estimate, CIA World Factbook), which isn't comparable with the child poverty rates elsewhere on this site.",
      footer: "Saint-Pierre-et-Miquelon as of November 2026. Sources are listed on the Sources tab." },
    // United Kingdom: its own button and nations. Child poverty is DWP's relative low income (children under 16).
    { name: "United Kingdom", file: "data/uk.csv", country: "UK", recordLabel: "Councils", textColumns: ["District ID", "Enrollment year"],
      groups: { column: "Nation", label: "United Kingdom",
        names: { E: "England", S: "Scotland", W: "Wales", N: "Northern Ireland" } },
      chart: { type: "scatter", x: "Percentage of Children Under 16 in Low Income", y: "Available Board Meetings" },
      compare: {
        title: "Child low income: councils with vs. without meetings found",
        by: "Available Board Meetings", metric: "Percentage of Children Under 16 in Low Income",
        withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found"
      },
      sizeYearNote: "Councils are grouped by pupils in state-funded schools: England January 2026 (register of schools), Scotland September 2025, Wales January 2025, Northern Ireland October 2025.",
      note: "{rows} UK education authorities: England's 153 upper-tier councils (counties, unitary authorities, metropolitan and London boroughs), Scotland's 32 and Wales's 22 councils, and Northern Ireland's Education Authority. The UK has no elected school boards; these councils (and Northern Ireland's Education Authority) run state schools, and their education or children's services committees are the closest thing. Child low income is the Department for Work and Pensions' share of children under 16 in relative low income before housing costs, financial year ending 2025, which isn't the same measure as the US or Canadian rates. Meetings found for {withMeetings} councils.",
      footer: "UK education authorities as of November 2026. Sources are listed on the Sources tab." }
  ],
  // "All" button: every US district, territory school system and Canadian board together.
  combined: {
    name: "All: United States, U.S. territories, Canada, Saint-Pierre-et-Miquelon and the United Kingdom", button: "All", recordLabel: "Districts and boards",
    textColumns: ["District ID"], metric: "Child poverty rate",
    measures: {
      us: "Children 5–17 in poverty (Census SAIPE 2024)",
      territories: "Children 5–17 in poverty (Census; 2020 Census for all but Puerto Rico)",
      canada: "Children 0–17 in low income (Statistics Canada LIM-AT, 2021 Census)",
      uk: "Children under 16 in relative low income before housing costs (DWP, financial year ending 2025)",
      france: "Unemployment rate, 2015 estimate (CIA World Factbook): a stand-in, since no poverty rate is published for Saint-Pierre-et-Miquelon"
    },
    chart: { type: "scatter", x: "Child poverty rate", y: "Available Board Meetings" },
    sizeYearNote: "Districts and boards are grouped by student enrollment: US districts 2023 (NCES); Canadian boards each province's latest published figures (none yet for PEI's French board or the Yukon First Nation School Board).",
    compare: {
      title: "Child poverty: with vs. without available board meetings (all countries)",
      by: "Available Board Meetings", metric: "Child poverty rate",
      withLabel: "With 1+ available meetings", withoutLabel: "With no available meetings"
    },
    note: "Every US school district, U.S. territory school system and Canadian school board on this site together ({rows}; meetings found for {withMeetings}). The child poverty rate isn't measured the same way everywhere: US districts use the Census share of children 5–17 in poverty, the territories mostly the 2020 Census, and Canada Statistics Canada's share of children 0–17 in low income (see the “Poverty measure” column). Meeting counts come from CivicSearch in the US and from the boards' own sites or YouTube channels in the territories and Canada. So treat comparisons across countries with care; the US, territory and Canada buttons have each one's full figures.",
    footer: "Built from the United States, U.S. territories and Canada data. Sources for all three are listed on the Sources tab."
  },
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
