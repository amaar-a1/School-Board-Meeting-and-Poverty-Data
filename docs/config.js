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
      sizeYearNote: "Boards are grouped by student enrollment from each province's latest published figures (see the “Enrollment year” column: mostly 2024–25 or 2025–26; Quebec September 2022; Saskatchewan September 30, 2024). A few boards' figures come from other sources and are noted in the “Enrollment note” column (the Northwest Territories' are full-time-equivalent grades 1–12). The Yukon First Nation School Board's figure covers 7 of its 11 schools, so it undercounts.",
      note: "{rows} Canadian school boards and school service centres in every province and territory. Canada has no site like CivicSearch, so meeting counts are the board meetings each board has posted on its own YouTube channel (meetings found for {withMeetings} boards; the rest show 0, which can also mean the board streams elsewhere). Low income is Statistics Canada's after-tax low-income measure (LIM-AT) for children ages 0–17 from the 2021 Census (2020 incomes), worked out for each board from the census subdivisions inside its border; see the “How poverty was calculated” column. These figures aren't comparable with the US child poverty rates. Enrollment comes from each province's latest published figures, with a few from other sources (see the “Enrollment note” column); the Yukon First Nation School Board's covers only 7 of its 11 schools.",
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
      localeNote: "Councils are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (children counted in the census, divided by their share of the population, over land area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Councils are grouped by pupils in state-funded schools: England January 2026 (register of schools), Scotland September 2025, Wales January 2025, Northern Ireland October 2025.",
      note: "{rows} UK education authorities: England's 153 upper-tier councils (counties, unitary authorities, metropolitan and London boroughs), Scotland's 32 and Wales's 22 councils, and Northern Ireland's Education Authority. The UK has no elected school boards; these councils (and Northern Ireland's Education Authority) run state schools, and their education or children's services committees are the closest thing. Child low income is the Department for Work and Pensions' share of children under 16 in relative low income before housing costs, financial year ending 2025, which isn't the same measure as the US or Canadian rates. Meetings are recordings of the council's education, schools or children's committee meetings (including its Schools Forum) on its own YouTube channel, found for {withMeetings} councils; many councils webcast on their own sites instead, which weren't counted, so 0 can also mean that.",
      footer: "UK education authorities as of November 2026. Sources are listed on the Sources tab." },
    // Ireland: its own button. No local child poverty rate, so Census 2022 unemployment stands in.
    { name: "Ireland", file: "data/ireland.csv", country: "IE", recordLabel: "Boards", textColumns: ["District ID"],
      chart: { type: "bar", x: "District", y: "Poverty rate (region, all ages)" },
      compare: { title: "Poverty rate (each board's region): boards with vs. without meetings found", by: "Available Board Meetings",
        metric: "Poverty rate (region, all ages)", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      sizeNote: "Enrollment by Education and Training Board isn't published openly, so boards can't be grouped by size.",
      localeNote: "Boards are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (children counted in the census, divided by their share of the population, over land area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      note: "Ireland's 16 Education and Training Boards (ETBs), the elected-and-appointed local boards that run about a quarter of post-primary schools (community colleges and community schools), Community National Schools and further education. Each covers one or more council areas; most primary and secondary schools are run by other patron bodies, so ETBs aren't a full equivalent of a US school board. Ireland publishes no local child poverty rate, so each board shows the overall at-risk-of-poverty rate (all ages, below 60% of the median income) of the Eurostat region it's in: Northern and Western, Southern, or Eastern and Midland. Boards in the same region share a figure, and it isn't comparable with the child poverty rates elsewhere on this site. Each board's local unemployment rate from Census 2022 is in its own column. No ETB posts its board meetings on YouTube (their channels show school and course videos); ETBs publish board minutes on their own websites instead, which weren't counted.",
      footer: "Irish Education and Training Boards as of November 2026. Sources are listed on the Sources tab." },
    // Norway: municipalities run schools. Child low income is the national statistics office's own measure.
    { name: "Norway", file: "data/norway.csv", country: "NO", recordLabel: "Municipalities", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Statistics Norway: children 0–17 in households with persistent low income (below 60% of the median, three-year period 2022–2024)", rules: "norway" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Eurostat's 2023 people per km² for each municipality; Finland's from children counted, divided by their share of the population, over the municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Municipalities are grouped by pupils in compulsory school (grades 1–10, municipal and private) in autumn 2025 (Statistics Norway).",
      note: "Norway's {rows} municipalities (kommuner), which run its primary and lower secondary schools; each has an elected council, and most have a committee for children and education (oppvekstutvalg or similar) that is the closest thing to a school board. Child low income is Statistics Norway's share of children 0–17 in households with persistent low income (below 60% of the median, over the three years 2022–2024), which isn't the same measure as the US, Canadian or other European rates; it isn't published for some small municipalities. For 13 small municipalities whose child rate isn't published, the all-ages rate is shown instead (see the Poverty note column). Enrollment is pupils in compulsory school (grades 1–10, municipal and private) in autumn 2025. Meetings are recordings on the municipality's own YouTube channel whose titles name its education or children's committee (in the country's language) and a meeting, found for {withMeetings} municipalities; children's councils, parent meetings and full council meetings aren't counted. Committee meetings are open, but many municipalities stream only on their own sites (for example through Kommunal-TV), which weren't counted. So 0 can also mean the meetings are recorded elsewhere.",
      footer: "Norway municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Sweden: municipalities run schools. Child low income is the national statistics office's own measure.
    { name: "Sweden", file: "data/sweden.csv", country: "SE", recordLabel: "Municipalities", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Statistics Sweden: people 0–19 with a low economic standard (household income below 60% of the median, adjusted for household size), 2024", rules: "sweden" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Eurostat's 2023 people per km² for each municipality; Finland's from children counted, divided by their share of the population, over the municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Municipalities are grouped by pupils in compulsory school (förskoleklass to year 9) living in the municipality, 2025 (Kolada).",
      note: "Sweden's {rows} municipalities (kommuner), which run most of its schools; each has an elected council and a board (nämnd) for education, often called barn- och utbildningsnämnden, which is the closest thing to a school board. Independent schools (friskolor) are run by their own owners. Child low income is Statistics Sweden's share of people 0–19 with a low economic standard in 2024 (household income below 60% of the median), which isn't the same measure as the US, Canadian or other European rates. Enrollment is pupils in compulsory school (förskoleklass to year 9) living in the municipality, 2025 (Kolada). Meetings are recordings on the municipality's own YouTube channel whose titles name its education or children's committee (in the country's language) and a meeting, found for {withMeetings} municipalities; children's councils, parent meetings and full council meetings aren't counted. Education boards there normally meet behind closed doors, so few are recorded. So 0 can also mean the meetings are recorded elsewhere.",
      footer: "Sweden municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Finland: municipalities run schools. Child low income is the national statistics office's own measure.
    { name: "Finland", file: "data/finland.csv", country: "FI", recordLabel: "Municipalities", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "THL (Sotkanet): children under 18 in low-income households (below 60% of the median), latest year 2022–2024", rules: "finland" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Eurostat's 2023 people per km² for each municipality; Finland's from children counted, divided by their share of the population, over the municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Municipalities are grouped by pupils in comprehensive school (grades 1–9), 2025 (Statistics Finland).",
      note: "Finland's {rows} municipalities (kunnat), which run almost all of its comprehensive schools; each has an elected council and an education committee (sivistyslautakunta or similar), the closest thing to a school board. Child low income is the share of children under 18 in low-income households (below 60% of the median), from THL's Sotkanet, latest year available (2022–2024), which isn't the same measure as the US, Canadian or other European rates. Where the child rate isn't published (mostly on Åland), the municipality's overall low-income rate is shown instead (see the Poverty note column). Enrollment is comprehensive school pupils in 2025 (Statistics Finland). Meetings are recordings on the municipality's own YouTube channel whose titles name its education or children's committee (in the country's language) and a meeting, found for {withMeetings} municipalities; children's councils, parent meetings and full council meetings aren't counted. Education committees there normally meet in closed session, so few are recorded. So 0 can also mean the meetings are recorded elsewhere.",
      footer: "Finland municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Denmark: municipalities run schools. Child low income is the national statistics office's own measure.
    { name: "Denmark", file: "data/denmark.csv", country: "DK", recordLabel: "Municipalities", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Statistics Denmark: children 0–17 in relative poverty (below 50% of the median), 2024", rules: "denmark" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Eurostat's 2023 people per km² for each municipality; Finland's from children counted, divided by their share of the population, over the municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Municipalities are grouped by pupils in primary and lower secondary school on 1 October 2025 (Statistics Denmark).",
      note: "Denmark's {rows} municipalities (kommuner), which run its public primary and lower secondary schools (folkeskoler); each has an elected council and a children and schools committee (børne- og skoleudvalg or similar), the closest thing to a school board. Child poverty is Statistics Denmark's share of children 0–17 in relative poverty in 2024 (below 50% of the median income, a stricter line than most countries on this site use), so it isn't comparable with the other rates. Christiansø, which isn't part of a municipality, shows Denmark's national child rate. Enrollment is pupils in primary and lower secondary school on 1 October 2025. Meetings are recordings on the municipality's own YouTube channel whose titles name its education or children's committee (in the country's language) and a meeting, found for {withMeetings} municipalities; children's councils, parent meetings and full council meetings aren't counted. Committees there meet behind closed doors by law, so few are recorded. So 0 can also mean the meetings are recorded elsewhere.",
      footer: "Denmark municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Netherlands: municipalities run schools. Child low income is the national statistics office's own measure.
    { name: "Netherlands", file: "data/netherlands.csv", country: "NL", recordLabel: "Municipalities", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "CBS: children in households below CBS's poverty line (its “not much but sufficient” budget), 2024", rules: "netherlands" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Eurostat's 2023 people per km² for each municipality; Finland's from children counted, divided by their share of the population, over the municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      sizeYearNote: "Municipalities are grouped by pupils in primary, special and secondary education living in the municipality, 2025/26 (CBS).",
      note: "The Netherlands' {rows} municipalities (gemeenten). Dutch schools are run by school boards (schoolbesturen), both public and private, which aren't tied to municipalities; the municipality funds school buildings, runs youth and education policy, and its elected council and committees (open to the public by law) are the closest local body with public meetings. Child poverty is the share of children in households below CBS's poverty line (its “not much but sufficient” budget) in 2024, which isn't the same measure as the US, Canadian or other European rates. Brielle, Hellevoetsluis and Westvoorne merged into Voorne aan Zee in 2023 and are shown as one. Enrollment is pupils in primary, special and secondary education living in the municipality, 2025/26 (CBS). Meetings are recordings on the municipality's own YouTube channel whose titles name its education or children's committee (in the country's language) and a meeting, found for {withMeetings} municipalities; children's councils, parent meetings and full council meetings aren't counted. Councils nearly all webcast on their own sites (Notubiz, Company Webcast and the like), which weren't counted. So 0 can also mean the meetings are recorded elsewhere.",
      footer: "Netherlands municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Iceland: municipalities run the compulsory schools; councils stream their meetings, where school matters come up.
    { name: "Iceland", file: "data/iceland.csv", country: "IS", recordLabel: "Municipalities", textColumns: ["District ID"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Children under 18 below 60% of the median income: Iceland's national rate (Eurostat), since no local rate is published", rules: "iceland" },
      chart: { type: "scatter", x: "Children", y: "Available Board Meetings" },
      compare: { title: "Child low income: municipalities with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      sizeNote: "Pupil counts by municipality aren't published, so municipalities can't be grouped by enrollment; the Children column is everyone aged 6–15, the compulsory school ages.",
      localeNote: "Municipalities are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (Statistics Iceland's population over each municipality's area): urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100.",
      note: "Iceland's {rows} municipalities (sveitarfélög), which run its compulsory schools (grunnskólar, ages 6–15). Their education committees (fræðsluráð or skólanefnd) meet in private, so the meeting count is the elected council's meetings (bæjarstjórn, sveitarstjórn or, in Reykjavík, borgarstjórn), where the committees' school business is approved and debated: recordings on the municipality's own YouTube channel, counted once per meeting, found for {withMeetings} municipalities. Many councils stream on their own websites or Facebook instead, which weren't counted, so 0 can also mean that. These are full council meetings, so they aren't directly comparable with the education-committee counts for the other Nordic countries. Iceland publishes no child poverty rate below the national level, so every municipality shows the national rate (Eurostat, 2020, the latest).",
      footer: "Icelandic municipalities as of November 2026. Sources are listed on the Sources tab." },
    // Switzerland: the 26 cantons run the schools; child social assistance rate by canton.
    { name: "Switzerland", file: "data/switzerland.csv", country: "CH", recordLabel: "Cantons", textColumns: ["District ID", "Enrollment year"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Children 0–17 receiving social assistance (Federal Statistical Office, 2025)", rules: "switzerland" },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Enrollment" },
      compare: { title: "Child social assistance: cantons with vs. without parliament sittings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ sittings found", withoutLabel: "With no sittings found" },
      localeNote: "Cantons are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (children divided by 0.19, their approximate share of the population, over the canton's area): urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100.",
      sizeYearNote: "Cantons are grouped by pupils in compulsory school, 2024/25 (Federal Statistical Office).",
      note: "Switzerland's {rows} cantons, which each run their own school system through an education department and school law. Many municipalities or school communities also elect a school board (Schulpflege, Schulkommission or commission scolaire), but there are about 2,000 of them and no poverty figures below the canton, so the site shows the cantons. Child poverty is the share of children 0–17 receiving social assistance in 2025 (Federal Statistical Office), which leaves out poor families not on assistance, so it's lower than income-based rates elsewhere. The meeting count is a stand-in: sittings of the cantonal parliament (Kantonsrat, Grosser Rat, Landrat, Grand Conseil or Gran Consiglio), which passes the canton's school law and budget, recorded on YouTube and counted once per day, found for {withMeetings} cantons; most cantonal parliaments stream on their own websites, so 0 often means that.",
      footer: "Swiss cantons as of November 2026. Sources are listed on the Sources tab." },
    // Germany: 400 districts and district-free cities (the school authorities), with each state's view.
    { name: "Germany", file: "data/germany.csv", country: "DE", recordLabel: "Districts", textColumns: ["District ID"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Children under 15 receiving basic income support (SGB II), 2023 (Bertelsmann Stiftung, Wegweiser Kommune)", rules: "germany", place: "State" },
      groups: { column: "State", label: "Germany",
        names: { BW: "Baden-Württemberg", BY: "Bavaria", BE: "Berlin", BB: "Brandenburg", HB: "Bremen", HH: "Hamburg", HE: "Hesse",
          MV: "Mecklenburg-Vorpommern", NI: "Lower Saxony", NW: "North Rhine-Westphalia", RP: "Rhineland-Palatinate", SL: "Saarland",
          SN: "Saxony", ST: "Saxony-Anhalt", SH: "Schleswig-Holstein", TH: "Thuringia" } },
      chart: { type: "scatter", x: "Percentage of Children in Low Income", y: "Children" },
      compare: { title: "Child poverty: districts with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      sizeNote: "Pupil counts by district aren't available openly in one file, so districts can't be grouped by size.",
      localeNote: "Districts are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from Eurostat's people per km² for each district: urban 2,000+, suburban 500–2,000, mixed town and country 100–500, rural under 100. They aren't the same as the US or Canadian locales.",
      note: "Germany's {rows} districts (Landkreise) and district-free cities (kreisfreie Städte, including Berlin and Hamburg). German schools are run jointly: each state employs the teachers and sets the curriculum, while districts and cities are the school authorities (Schulträger) that build and run the schools, overseen by a school committee (Schulausschuss) of the elected council, the closest thing to a school board. Child poverty is the share of children under 15 receiving basic income support (SGB II) in 2023, from the Bertelsmann Stiftung's Wegweiser Kommune; it leaves out families on other benefits, so it isn't the same as the US, Canadian or other European rates. Meeting counts haven't been gathered, so every district shows 0.",
      footer: "German districts as of November 2026. Sources are listed on the Sources tab." },
    // New Zealand: every school has its own elected board, so the site shows Stats NZ's 12 child poverty areas.
    { name: "New Zealand", file: "data/new-zealand.csv", country: "NZ", recordLabel: "Areas", textColumns: ["District ID"],
      simple: { pov: "Percentage of Children in Low Income", children: "Children", measure: "Stats NZ: children in households below 60% of the median income before housing costs, year ended June 2025", rules: "newzealand" },
      chart: { type: "bar", x: "District", y: "Percentage of Children in Low Income" },
      compare: { title: "Child low income: areas with vs. without meetings found", by: "Available Board Meetings",
        metric: "Percentage of Children in Low Income", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      sizeNote: "Enrollment by area isn't included (the Ministry of Education's school directory refused automated downloads), so areas can't be grouped by size.",
      localeNote: "Areas are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (children divided by 0.22, their approximate share of the population, over the area): urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100. Whole regions are mostly countryside, so nearly all show as rural.",
      note: "New Zealand has no school districts: each of its roughly 2,500 state and state-integrated schools is run by its own elected school board (parents, staff and, in secondary schools, a student), so there are far too many boards, with too few recordings, to count here. Instead, the site shows the {rows} areas Stats NZ publishes child poverty for (regional councils, some combined), with 0 meetings. Child low income is the share of children in households below 60% of the median income before housing costs, year ended June 2025; regional figures have wide sampling errors (several points either way).",
      footer: "New Zealand child poverty areas as of November 2026. Sources are listed on the Sources tab." },
    // Small island countries and territories: one education ministry or department each, so one "district" each.
    { name: "Islands and microstates", button: "Islands & microstates", file: "data/islands.csv", country: "ISLE", recordLabel: "Islands",
      textColumns: ["District ID", "Enrollment year"], localePrefix: "Islands",
      simple: { pov: "Poverty rate or stand-in", children: "Children Ages 0-14 (estimated)", measureColumn: "Poverty measure", rules: "islands", place: "Region" },
      groups: { column: "Region", label: "Islands and microstates",
        names: { CAR: "Caribbean", PAC: "Pacific", EUR: "Europe and the North Atlantic", ASI: "Asia and the Indian Ocean", AFR: "Africa and the South Atlantic", MIC: "European microstates" } },
      chart: { type: "scatter", x: "Poverty rate or stand-in", y: "Enrollment" },
      compare: { title: "Poverty (or stand-in): islands with vs. without legislature sittings found", by: "Available Board Meetings",
        metric: "Poverty rate or stand-in", withLabel: "With 1+ meetings found", withoutLabel: "With no meetings found" },
      sizeYearNote: "Islands are grouped by primary and secondary enrollment (World Bank / UNESCO, latest year with both; see the Enrollment year column).",
      localeNote: "Islands are grouped by an estimated locale (see below).",
      localeDef: "Locales are estimates from population density (population over land area, CIA World Factbook): urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100.",
      note: "{rows} small island countries and territories, and the European microstates (Luxembourg, Liechtenstein, Monaco, Andorra and San Marino); the U.S. territories and Saint-Pierre-et-Miquelon have their own views. Each runs its schools through one government education ministry or department, so each counts as a single “district”; none has elected local school boards like the US or Canada, Poverty figures are the best available for each place and aren't comparable: children below 60% of the median income for Malta, Cyprus and Luxembourg (Eurostat); otherwise the share of people below the country's own poverty line (World Bank, or the CIA World Factbook, sometimes from old surveys); and where neither exists, the unemployment rate as a stand-in. Saint-Barthélemy and Saint-Martin have no figure: none was found from INSEE, the World Bank or the Factbook. The “Poverty measure” column names each one and its year. None has a school board that meets in public, so, as for Saint-Pierre-et-Miquelon, the meeting count is a stand-in: recorded sittings (and committee meetings) of the elected legislature (parliament, house of assembly or territorial assembly), which passes the education budget and laws, counted once per day on its YouTube channel, found for {withMeetings} islands. Where only a government channel or public broadcaster posts them, just videos whose titles name the legislature count. Many legislatures stream on their own sites instead (for example Tynwald and the States of Guernsey), so 0 can also mean that, and these counts aren't comparable with school board meetings elsewhere.",
      footer: "Islands and microstates as of November 2026. Sources are listed on the Sources tab." }
  ],
  // "All" button: every US district, territory school system and Canadian board together.
  combined: {
    name: "All: United States, U.S. territories, Canada, Saint-Pierre-et-Miquelon, the United Kingdom, Ireland, the Nordic countries (with Iceland), the Netherlands, Switzerland, Germany, New Zealand and island countries", button: "All", recordLabel: "Districts and boards",
    textColumns: ["District ID"], metric: "Child poverty rate",
    measures: {
      us: "Children 5–17 in poverty (Census SAIPE 2024)",
      territories: "Children 5–17 in poverty (Census; 2020 Census for all but Puerto Rico)",
      canada: "Children 0–17 in low income (Statistics Canada LIM-AT, 2021 Census)",
      uk: "Children under 16 in relative low income before housing costs (DWP, financial year ending 2025)",
      ireland: "Overall at-risk-of-poverty rate, all ages, of the board's region (Eurostat, 2025): no local or child rate is published in Ireland",
      france: "Unemployment rate, 2015 estimate (CIA World Factbook): a stand-in, since no poverty rate is published for Saint-Pierre-et-Miquelon"
    },
    chart: { type: "scatter", x: "Child poverty rate", y: "Available Board Meetings" },
    sizeYearNote: "Districts and boards are grouped by student enrollment: US districts 2023 (NCES); Canadian boards each province's latest published figures (a few from other sources, noted in the Enrollment note column).",
    compare: {
      title: "Child poverty: with vs. without available board meetings (all countries)",
      by: "Available Board Meetings", metric: "Child poverty rate",
      withLabel: "With 1+ available meetings", withoutLabel: "With no available meetings"
    },
    note: "Every school district, board and council-level body on this site together ({rows}; meetings found for {withMeetings}): US school districts, U.S. territory school systems, Canadian school boards, Saint-Pierre-et-Miquelon, UK councils, Irish Education and Training Boards, and the municipalities that run schools in Norway, Sweden, Finland and Denmark (and the Dutch municipalities, which fund but don't run schools). The child poverty rate isn't measured the same way anywhere: each row's “Poverty measure” column names its own, Ireland uses its regions' overall poverty rates, and Saint-Pierre-et-Miquelon unemployment as a stand-in. Meeting counts come from CivicSearch in the US and from the bodies' own sites or YouTube channels elsewhere (for the Nordic countries and the Netherlands, their education committees' recordings; none yet for Germany, New Zealand or the islands). So treat comparisons across countries with care; each country's button has its full figures.",
    footer: "Built from every country's data on this site. Sources are listed on the Sources tab."
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
