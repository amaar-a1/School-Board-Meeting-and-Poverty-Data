// Sources shown on the page, grouped. Add `url` to an item to make it a link.
// `only: "<data set name>"` (or a list of names) on a group or item shows it just for those data sets.
window.SOURCES = [
  {
    only: ["Texas", "United States"],
    group: "Census data (children ages 5–17 and children in poverty)",
    items: [
      { only: "Texas", title: "Census SAIPE 2024 Texas school district file", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/sd24-tx.txt" },
      { title: "Census SAIPE 2024 school district estimates page, which describes the file layout", url: "https://www.census.gov/data/datasets/2024/demo/saipe/2024-school-districts.html" },
      { title: "SAIPE school district overview, which confirms the ages 5–17 measures", url: "https://census.gov/programs-surveys/saipe/technical-documentation/methodology/school-districts/overview-school-district.html" },
      { only: "United States", title: "Census SAIPE 2024 file for all US school districts", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/ussd24.csv" },
      { only: "United States", title: "Census SAIPE 2024 state and county estimates (all-ages poverty rate, used for the 5 districts with no children ages 5–17; see the Notes column)", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-state-and-county/est24all.txt" }
    ]
  },
  {
    group: "Meeting counts (available board meetings)",
    items: [
      { only: "Texas", title: "CivicSearch Texas district list", url: "https://schools.civicsearch.org/cities" },
      { only: "Texas", title: "Individual CivicSearch district pages, such as Alamo Heights ISD. All 74 Texas district pages were checked.", url: "https://schools.civicsearch.org/alamo-heights-isd-texas" },
      { only: "United States", title: "CivicSearch school district list", url: "https://schools.civicsearch.org/cities" },
      { only: "United States", title: "CivicSearch district list data (the meeting counts behind the district list, for every state; downloaded daily)", url: "https://schools.civicsearch.org/api/get_place_list" },
      { only: "United States", title: "USLege school board coverage, such as Carrollton-Farmers Branch ISD (checked, not used for counts)", url: "https://www.uslege.ai/tracking/carrollton-farmers-branch-independent-school-district" }
    ],
    note: "USLege covers about 60 school districts nationwide and counts only the last six months of meetings, so its numbers aren't comparable with CivicSearch's and weren't used."
  },
  {
    group: "Enrollment and urban/suburban/rural type",
    items: [
      { title: "NCES Common Core of Data 2023 school district directory (enrollment and locale codes), via the Urban Institute Education Data API", url: "https://educationdata.urban.org/documentation/school-districts.html" },
      { only: "United States", title: "NCES 2023 directory data for all US school districts", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/" },
      { only: "United States", title: "Land area of each school district (for population density): Census Bureau, 2024 Gazetteer files for unified, elementary and secondary school districts (ALAND); merged districts and the territories from their map borders", url: "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html" },
      { only: "United States", title: "NCES Private School Universe Survey (PSS) 2021-22, public-use school file: each private school's students and location, placed in the unified or elementary district whose border contains it (for the map's share of pupils in public schools; data-prep/prep_us_private.py)", url: "https://nces.ed.gov/surveys/pss/pssdata.asp" },
      { only: "United States", title: "NCES 2018–2022 directory data, used for the latest enrollment or locale of districts missing them in 2023 (e.g., New York City)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2022/" },
      { only: "U.S. territories", title: "NCES 2023 directory data (schools, enrollment and locale for the territories: Puerto Rico, Guam, Northern Mariana Islands, U.S. Virgin Islands, American Samoa)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/" },
      { only: "U.S. territories", title: "NCES 2021 directory data (Guam enrollment: 26,619; NCES has none for Guam after 2021)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2021/?fips=66" },
      { only: "U.S. territories", title: "NCES 2020 directory data (American Samoa enrollment: 10,246; NCES has none for American Samoa after 2020)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2020/?fips=60" },
      { only: "U.S. territories", title: "Population (for the map's density): Census Bureau, 2020 Census (Puerto Rico 3,285,874) and 2020 Island Areas Censuses (Guam 153,836; Northern Mariana Islands 47,329; St. Croix 41,004; St. Thomas and St. John 46,142; American Samoa 49,710)", url: "https://www.census.gov/programs-surveys/decennial-census/decade/2020/planning-management/release/2020-island-areas-data-products.html" }
    ]
  },
  {
    only: "U.S. territories",
    group: "U.S. territories: school boards, children and poverty",
    items: [
      { title: "Guam Department of Education YouTube channel, Live tab (Guam Education Board meeting recordings; 21 meetings counted October 30, 2026, including a stream titled “special meeting 11/06/25”)", url: "https://www.youtube.com/@guamdepartmentofeducation5142/streams" },
      { title: "Guam Education Board meeting notice naming the YouTube channel as its live stream (June 16, 2026 meeting)", url: "https://notices.guam.gov/notice_detail/9093" },
      { title: "Guam Education Board agenda for December 16, 2025, which approves the minutes of the November 6, 2025 special meeting (confirms that stream was a board meeting)", url: "https://notices.guam.gov/notice_detail/7906" },
      { title: "CNMI Public School System YouTube channel, Live tab (CNMI State Board of Education meeting recordings; 6 board meetings counted October 30, 2026, committee meetings left out)", url: "https://www.youtube.com/channel/UCkbpGWkvnelMHKwyFGpwf0w/streams" },
      { title: "CNMI Public School System videos page and board meeting notices (meetings are held on Zoom; no recordings posted)", url: "https://cnmipss.org/videos" },
      { title: "Virgin Islands Board of Education meeting agendas and minutes (no recordings posted)", url: "https://myviboe.com/meeting-agendas-minutes/" },
      { title: "Virgin Islands Board of Education News Room (meeting notices)", url: "https://myviboe.com/news-room/" },
      { title: "Virgin Islands Board of Education meeting notices in the St. Thomas Source (meetings held in person and on Microsoft Teams; no recordings linked)", url: "https://stthomassource.com/content/2026/08/07/virgin-islands-board-of-education-announces-emergency-board-meeting/" },
      { title: "KVZK-TV, American Samoa's government station (checked; no Board of Education meeting recordings found)", url: "https://www.samoanews.com/kvzk-tv" },
      { title: "Government Access Channel – Virgin Islands on YouTube (checked; no board meeting recordings)", url: "https://www.youtube.com/channel/UCUeosYkcAS4HVKSfbLNR0FA" },
      { title: "American Samoa Department of Education website (could not be reached October 30, 2026; YouTube searches found no board meeting recordings)", url: "https://www.doe.as/" },
      { title: "Puerto Rico Department of Education: run as a cabinet department, with no school board" },
      { title: "Puerto Rico Senate YouTube channel (education committee public hearings; 7 counted, Nov. 3, 2026). Puerto Rico has no school board, so legislative education hearings stand in", url: "https://www.youtube.com/channel/UCg90Gzk-QoCxYUNYmAUasWA" },
      { title: "Puerto Rico House of Representatives YouTube channel (education committee hearings and markup sessions; 14 counted)", url: "https://www.youtube.com/channel/UCm0SWjunIA5PDT9l4qW59Kw" },
      { title: "Google search summary of how each territory's schools are run and which boards post meetings online (searched by the project team, October 30, 2026); used to find the channels above" },
      { title: "CivicSearch school district list data (checked October 30, 2026; it lists no school boards in the territories, so their meeting counts come from the boards’ own channels instead)", url: "https://schools.civicsearch.org/api/get_place_list" },
      { title: "2020 Census of Guam, Demographic and Housing Characteristics File (poverty status in 2019 by age by sex, table PCT78: children ages 5–17 and children in poverty)", url: "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas/guam/demographic-and-housing-characteristics-file/" },
      { title: "2020 Census of the Northern Mariana Islands, Demographic and Housing Characteristics File (table PCT77)", url: "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas/commonwealth-of-the-northern-mariana-islands/demographic-and-housing-characteristics-file/" },
      { title: "2020 Census of the U.S. Virgin Islands, Demographic and Housing Characteristics File (table PCT75, by island: St. Croix, and St. Thomas plus St. John)", url: "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas/us-virgin-islands/demographic-and-housing-characteristics-file/" },
      { title: "2020 Census of American Samoa, Demographic and Housing Characteristics File (table PCT77)", url: "https://www2.census.gov/programs-surveys/decennial/2020/data/island-areas/american-samoa/demographic-and-housing-characteristics-file/" },
      { title: "Census press release on Guam's 2020 data (used to check the Guam totals: 145,543 people, 29,408 below poverty)", url: "https://www.census.gov/newsroom/press-releases/2023/2020-dhc-summary-file-guam.html" },
      { title: "Census press release on American Samoa's 2020 data (used to check its totals: 48,506 people, 26,480 below poverty)", url: "https://www.census.gov/newsroom/press-releases/2023/2020-dhc-summary-file-american-samoa.html" },
      { title: "Census SAIPE 2024 file for all US school districts (Puerto Rico's children ages 5–17 and children in poverty; no other territory is in the file)", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/ussd24.csv" },
      { title: "Census SAIPE estimation details for Puerto Rico (its figures come from the Puerto Rico Community Survey)", url: "https://www.census.gov/programs-surveys/saipe/technical-documentation/methodology/puerto-rico.html" }
    ],
    note: "Territory meeting counts come from the boards' YouTube channels, not CivicSearch, so they aren't directly comparable with the states' counts."
  },
  {
    group: "Borders in disputed areas",
    items: [
      { title: "De facto control: Natural Earth's default view, which draws each area as part of the country that administers it", url: "https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/" }
    ],
    note: "Places are drawn where they are actually administered, not by claims, since claims overlap (in Kashmir, for example, India's, Pakistan's and China's). So Aksai Chin shows as part of China and Pakistan-administered Kashmir as part of Pakistan, though India claims both; Taiwan as a country of its own; Israel's local authorities in the West Bank settlements and the Golan Heights, which Israel administers, under Israel, with their status noted; and Abkhazia and South Ossetia, occupied by Russia and not administered by Georgia, in grey with no Georgian figures. Each country's note says where its borders are disputed."
  },
  {
    group: "Map (district borders)",
    items: [
      { title: "Grey outlines for countries the site doesn't cover: Natural Earth 1:50m admin-0 countries (public domain; data-prep/build_world.py)", url: "https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/" },
      { title: "Census Bureau 2024 cartographic boundary files: unified school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_unsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: elementary school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_elsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: secondary school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_scsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: states and territories (outlines for Guam, the Northern Mariana Islands and American Samoa)", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: counties (the U.S. Virgin Islands' islands, for its two districts)", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip" },
      { title: "NCES 2023 school district directory (supervisory union number for each Vermont town district, used to show its union's figures)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/?fips=50" },
      { title: "VCGI: Vermont supervisory union boundaries (checked; the map builds the same unions from their member districts)", url: "https://maps.vcgi.vermont.gov/arcgis/rest/services/EGC_services/OPENDATA_VCGI_BOUNDARIES_SP_NOCACHE_v1/MapServer/55" },
      { title: "Region 20 (Connecticut): Goshen, Litchfield, Morris and Warren merged Region 6 and Litchfield Public Schools in 2024", url: "https://www.rsd6.org/page/who-we-are" },
      { title: "Henry Hudson Regional School District (New Jersey) became PreK–12 in 2024, merging Atlantic Highlands and Highlands", url: "https://en.wikipedia.org/wiki/Henry_Hudson_Regional_School_District" },
      { title: "St. Anne Unit District 24 (Illinois) replaced districts 256 and 302 in 2024", url: "https://www.shawlocal.com/daily-journal/news/2024/07/27/st-annes-new-school-district-up-and-running/" },
      { title: "Barnwell County school consolidation (South Carolina)", url: "https://www.wrdw.com/2024/06/26/people-leave-upset-after-barnwell-county-consolidated-school-meeting" },
      { title: "Nebraska Department of Education unification report (South Central Nebraska Unified 5 covers Lawrence-Nelson and Sandy Creek)", url: "https://www.education.ne.gov/wp-content/uploads/2023/11/UnificationReport_2023-24.pdf" },
      { title: "Census SAIPE 2024 county estimates (all-ages poverty rate shown for 8 districts the district file leaves out: Defense Department base schools at Fort Jackson and Marine Corps Air Station Beaufort, districts with no schools in Montana, North Dakota and Oklahoma, Tanana City in Alaska and Spring Creek ISD in Texas)", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-state-and-county/est24all.txt" },
      { title: "Background map: © OpenStreetMap contributors, © CARTO", url: "https://carto.com/attributions" }
    ],
    note: "Borders were simplified with mapshaper so the map loads quickly; they are drawn with Leaflet."
  },
  {
    only: "United States",
    group: "Board meetings from other sources (DC, Hawaiʻi, Vermont; not CivicSearch)",
    items: [
      { title: "DC State Board of Education on-demand meeting videos, DC Office of Cable Television (106 meetings, Sept. 2016 – June 2026)", url: "https://entertainment.dc.gov/page/demand-videos-dc-state-board-education-and-dcps-special-events" },
      { title: "Hawaiʻi State Board of Education meeting recordings (4 general business and special meetings, May – Oct. 2026)", url: "https://boe.hawaii.gov/meeting-recordings/" },
      { title: "Montpelier Roxbury Public Schools board meeting videos, recorded by ORCA Media (93 meetings, Feb. 2022 – Aug. 2026; one page per year)", url: "https://www.mrpsvt.org/2025-videos" },
      { title: "PEGTV (Rutland) school board video playlist: Rutland City, Otter Valley (Rutland Northeast) and Mill River boards, 1 recent meeting each", url: "https://videoplayer.telvue.com/player/MFXsvSYzjQOlecorW3Sq8GyBkhIm0OQN/playlists/6207" },
      { title: "Checked but not counted: South Burlington and Milton school district sites and ORCA Media's site block automated visits; South Burlington's board says its recordings are on The Media Factory and Facebook", url: "https://sbschools.net/page/school-board" }
    ],
    note: "Other Vermont districts may post meetings on their own websites or local public-access TV stations (for example The Media Factory, CCTV or ORCA Media), which haven't been checked, so Vermont's counts are incomplete. These counts are in the separate “Other Board Meetings” column. The Available Board Meetings column, and every total, comparison, chart and filter, use CivicSearch only; the map's meetings colors use these counts where CivicSearch has none."
  },
  {
    only: "Norway",
    group: "Norway: municipalities, child low income and pupils",
    items: [
      { title: "Child low income: Statistics Norway table 12944, persistent low income (EU scale, 60% of the median), children 0–17, 2022–2024", url: "https://www.ssb.no/en/statbank/table/12944/" },
      { title: "Where the child rate isn't published (13 small municipalities): Statistics Norway table 12944, all ages, 2022–2024", url: "https://www.ssb.no/en/statbank/table/12944/" },
      { title: "Pupils: Statistics Norway table 11980, pupils in compulsory school, 2025 (all schools; public = “Kommunal”, municipal schools)", url: "https://www.ssb.no/en/statbank/table/11980/" },
      { title: "Borders and density: Eurostat GISCO Local Administrative Units (LAU) 2023", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" }
    ],
    note: "Locales are estimates from Eurostat's 2023 people per km² for each municipality: urban 2,000+, suburban 500–2,000, mixed 100–500, rural under 100. Built by data-prep/build_nordic.py. Norway renumbered its municipalities in 2024, so the figures are matched to the 2023 borders by name; Haram, split from Ålesund in 2024, isn't shown on its own: its area is drawn as part of Ålesund, whose figures are for Ålesund without Haram."
  },
  {
    only: "Sweden",
    group: "Sweden: municipalities, low economic standard and pupils",
    items: [
      { title: "Low economic standard: Statistics Sweden (SCB) table TAB6685, people 0–19 with household income below 60% of the median, 2024", url: "https://www.statistikdatabasen.scb.se/" },
      { title: "Pupils: Kolada key figure N15835, pupils in compulsory school (F–9) by home municipality, 2025", url: "https://www.kolada.se/" },
      { title: "Public-school pupils: Kolada N15831 (from SCB), 2025: the share of resident pupils (förskoleklass to year 9) at an independent (fristående) school or another municipality's school; the rest, at their own municipality's schools, count as public", url: "https://www.kolada.se/verktyg/fri-sokning/?kpis=N15831" },
      { title: "Borders and density: Eurostat GISCO Local Administrative Units (LAU) 2023", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" }
    ],
    note: "Locales are estimates from Eurostat's 2023 people per km² for each municipality: urban 2,000+, suburban 500–2,000, mixed 100–500, rural under 100. Built by data-prep/build_nordic.py."
  },
  {
    only: "Finland",
    group: "Finland: municipalities, child low income and pupils",
    items: [
      { title: "Child low income: THL Sotkanet indicator 228, children under 18 in low-income households, 2022–2024 (latest year per municipality)", url: "https://sotkanet.fi/sotkanet/en/metadata/indicators/228" },
      { title: "Where the child rate isn't published (Åland and other small municipalities): THL Sotkanet indicator 3099, the municipality's overall low-income rate", url: "https://sotkanet.fi/sotkanet/en/metadata/indicators/3099" },
      { title: "Pupils: Statistics Finland table 133w, comprehensive school pupils, 2025", url: "https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__opiskt/" },
      { title: "Public-school share: Statistics Finland table 125j, 2025: pupils at comprehensive, special and combined schools by owner type; public = municipal, joint-municipal and state schools, private = privately owned", url: "https://pxdata.stat.fi/PxWeb/pxweb/fi/StatFin/StatFin__kjarj/statfin_kjarj_pxt_125j.px/" },
      { title: "Borders and density: Eurostat GISCO Local Administrative Units (LAU) 2023", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" }
    ],
    note: "Locales are estimates: population (children under 18 divided by 0.19, their approximate share of Finland's population) over each municipality's area from the Eurostat borders, since Eurostat's Finnish density figures are wrong; urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100. Lakes count in the area, so some lake-district municipalities look more rural than they are."
  },
  {
    only: "Denmark",
    group: "Denmark: municipalities, child poverty and pupils",
    items: [
      { title: "Child poverty: Statistics Denmark table LABY07, children 0–17 in relative poverty (50% of the median), 2024", url: "https://www.statbank.dk/LABY07" },
      { title: "Pupils: Statistics Denmark table LABY23, pupils in primary and lower secondary school on 1 October 2025; public = public basic schools (folkeskoler) and other schools (mostly municipal special schools); private = friskoler and efterskoler", url: "https://www.statbank.dk/LABY23" },
      { title: "Borders and density: Eurostat GISCO Local Administrative Units (LAU) 2023", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" }
    ],
    note: "Locales are estimates from Eurostat's 2023 people per km² for each municipality: urban 2,000+, suburban 500–2,000, mixed 100–500, rural under 100. Built by data-prep/build_nordic.py."
  },
  {
    only: "Netherlands",
    group: "Netherlands: municipalities, child poverty and pupils",
    items: [
      { title: "Child poverty: CBS table 86132NED, children in poverty (the “not much but sufficient” criterion), 2024", url: "https://opendata.cbs.nl/statline/#/CBS/nl/dataset/86132NED/table" },
      { title: "Pupils: CBS table 85701NED, pupils by municipality of residence (primary, special and secondary), 2025/26", url: "https://opendata.cbs.nl/statline/#/CBS/nl/dataset/85701NED/table" },
      { title: "Public-school share (Netherlands): DUO open education data, pupils per primary and special school site, 2025 (Leerlingen po per vestiging), with each site\u2019s municipality and denomination from DUO\u2019s school address lists. Public = openbaar schools, run by a public authority; bijzonder schools (Catholic, Protestant, general and other) are publicly funded but privately run, so they count as private, and the few joint (samenwerking) schools aren\u2019t counted as public. DUO\u2019s per-site secondary file stops at 2018, so the primary share is applied to all pupils", url: "https://onderwijsdata.duo.nl/dataset/cf80e90d-ed19-4a10-a138-00c5c345cb5e" },
      { title: "Borders and density: Eurostat GISCO Local Administrative Units (LAU) 2023", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" }
    ],
    note: "Locales are estimates from Eurostat's 2023 people per km² for each municipality: urban 2,000+, suburban 500–2,000, mixed 100–500, rural under 100. Built by data-prep/build_nordic.py. Voorne aan Zee (2023) is drawn from its three former municipalities' borders."
  },
  {
    only: "Germany",
    group: "Germany: districts, child poverty, population and pupils",
    items: [
      { title: "Child poverty: Bertelsmann Stiftung, Wegweiser Kommune, indicator “Kinderarmut” (children under 15 receiving SGB II basic income support), 2023, CC0 licence", url: "https://www.wegweiser-kommune.de/daten/kinderarmut" },
      { title: "Children under 15: Eurostat demo_r_pjanaggr3 (population on 1 January by broad age group, NUTS 3)", url: "https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjanaggr3/default/table" },
      { title: "Density: Eurostat demo_r_d3dens (population density, NUTS 3)", url: "https://ec.europa.eu/eurostat/databrowser/view/demo_r_d3dens/default/table" },
      { title: "Enrollment: Statistische Ämter des Bundes und der Länder, Regionaldatenbank Deutschland, table 21111-01-03-4 (pupils at general schools by school type and district, start of the 2024/25 school year), Datenlizenz Deutschland – Namensnennung 2.0", url: "https://www.regionalstatistik.de/genesis/online?operation=table&code=21111-01-03-4" },
      { title: "Meetings: each district's or city's own YouTube channel (in the “Meetings source” column), found with data-prep/nordic_youtube.py and filtered in data-prep/build_germany.py", url: "https://www.youtube.com/" },
      { title: "Borders: Eurostat GISCO NUTS 2021, level 3, 1:10 million", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics" }
    ],
    note: "Wegweiser Kommune's districts were matched to the NUTS borders by name (data-prep/inputs/germany/de_ww_search.json); six that the search missed were matched by hand. The Regionaldatenbank's districts (German district codes) were matched to the NUTS districts by name within each state, keeping each city apart from the surrounding district of the same name; Eisenach, merged into the Wartburgkreis in 2021, is counted there. Built by data-prep/build_germany.py."
  },
  {
    only: "New Zealand",
    group: "New Zealand: child poverty areas",
    items: [
      { title: "Meetings (stand-in): recorded meetings on the YouTube channels of each area's regional or unitary council: Northland, Auckland, Waikato, Bay of Plenty, Gisborne, Hawke's Bay, Taranaki, Horizons, Greater Wellington, Tasman, Nelson, Marlborough, West Coast, Environment Canterbury, Otago and Environment Southland (listed November 2026)", url: "https://www.youtube.com/channel/UCXye5ro6lyuabv0MhUU8Guw" },
      { title: "Child low income: Stats NZ, Child poverty statistics, year ended June 2025, Table 4.02 (below 60% of the median income before housing costs, by regional council area)", url: "https://www.stats.govt.nz/information-releases/child-poverty-statistics-year-ended-june-2025/" },
      { title: "Enrollment: students enrolled in primary and secondary schools by region, July 2025 (Ministry of Education roll returns), via Figure.NZ", url: "https://figure.nz/chart/POTlO8r1L2X6mKJc" },
      { title: "Public-school share: Ministry of Education, New Zealand Schools Directory, rolls at 1 October 2026: the share of each region\u2019s pupils at state schools, applied to the July 2025 enrollment. State-integrated schools (mostly Catholic, run with a proprietor), charter schools and private schools count as private, the same who-runs-it rule as Ireland, Belgium, the Netherlands and Spain", url: "https://www.educationcounts.govt.nz/directories/list-of-nz-schools" },
      { title: "Borders: Natural Earth 1:10m admin-1 states and provinces (regions merged where Stats NZ combines them)", url: "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/" }
    ],
    note: "Enrollment for combined areas adds up their regions. The Chatham Islands aren't in Stats NZ's regional figures. Built by data-prep/build_nz.py."
  },
  {
    only: "Islands and microstates",
    group: "Islands and microstates",
    items: [
      { title: "Tokelau pupils (estimated, 341): Tokelau National Statistics Office, 2016 Census of Population and Dwellings: children aged 5–14 in Tokelau on census night (287; Tables about demography, table 1.1.2) plus people aged 15 and over still at school (54; Tables about education, table 4.1)", url: "https://www.tokelau.org.nz/Stats.html" },
      { title: "Pitcairn Islands pupils (0): Jeff Zhou, “Education in the Pitcairn Islands”, The Borgen Project: Pulau School closed in 2022 for lack of children, the last pupil moved to boarding school in New Zealand, and a United Nations working paper reports no children educated in the local school", url: "https://borgenproject.org/education-in-the-pitcairn-islands/" },
      { title: "Niue pupils: Niue High School, 214 students in 2019 (Niue Statistics Office)", url: "https://niuestatistics.nu/social/education/niue-high-school/" },
      { title: "Niue pupils: Niue Primary School, years 1–6 in term 4 of 2005, 178 (early childhood education left out; Niue Statistics Office)", url: "https://niuestatistics.nu/social/education/early-childhood-education-and-niue-primary-school/" },
      { title: "Public-school share: 100% where the islands have only government schools (Christmas Island, Cocos (Keeling) Islands, Svalbard, the Falklands, Niue, Tokelau); Norfolk Island 262 of 265 pupils at government schools (2021 Census)" },
      { title: "Falkland Islands pupils (estimated): residents aged 5–15, the compulsory school ages (398), Falkland Islands Government, Policy Department, 2021 Census Tables, table 2b (population by single years of age); used non-commercially, as its terms allow", url: "https://www.gov.fk/policy/2021-census/" },
      { title: "Svalbard pupils: Statistics Norway, table 11980, pupils in compulsory school, Longyearbyen, 2025 (194)", url: "https://www.ssb.no/en/statbank/table/11980/" },
      { title: "Children below 60% of the median income (Malta, Cyprus): Eurostat ilc_li02", url: "https://ec.europa.eu/eurostat/databrowser/view/ilc_li02/default/table" },
      { title: "National poverty line, unemployment, population, enrollment (primary and secondary): World Bank World Development Indicators (SI.POV.NAHC, SL.UEM.TOTL.ZS, SP.POP.TOTL, SP.POP.0014.TO.ZS, SE.PRM.ENRL, SE.SEC.ENRL); public-school pupils from the shares at private schools, primary and secondary (SE.PRM.PRIV.ZS, SE.SEC.PRIV.ZS, UNESCO Institute for Statistics), same year or nearest within three years; Curaçao left out (UNESCO shows no private pupils, though most of its schools are run by church school boards)", url: "https://data.worldbank.org/" },
      { title: "Saint-Martin and Saint-Barthélemy unemployment: IEDOM, annual economic reports 2025 (Rapport annuel économique de Saint-Martin, de Saint-Barthélemy)", url: "https://www.iedom.fr/Rapport-annuel-economique-de-Saint-Martin-2025" },
      { title: "Norfolk Island unemployment and pupils (155 residents in primary and 110 in secondary school): Australian Bureau of Statistics, 2021 Census QuickStats (Norfolk Island), CC BY 4.0", url: "https://www.abs.gov.au/census/find-census-data/quickstats/2021/SAL90004" },
      { title: "Where the World Bank has none: CIA World Factbook (2026 edition, and the November 2023 edition for poverty and unemployment), via the factbook.json archive", url: "https://github.com/factbook/factbook.json" },
      { title: "Meetings (stand-in): each legislature's YouTube channel, found with data-prep/islands_youtube.py and checked by hand (listed in the “Meetings source” column); sittings counted once per day", url: "https://www.youtube.com/" },
      { title: "Borders: Natural Earth 1:10m admin-0 countries", url: "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/" },
      { title: "Bonaire, Sint Eustatius and Saba, child poverty: Statistics Netherlands (CBS), “Poverty on Bonaire, St Eustatius and Saba declined in 2024”", url: "https://www.cbs.nl/en-gb/news/2026/29/poverty-on-bonaire-st-eustatius-and-saba-declined-in-2024" },
      { title: "Bonaire, Sint Eustatius and Saba, population by age (1 January 2026) and pupils (2025/26): CBS StatLine tables 83698NED and 84732NED", url: "https://opendata.cbs.nl/statline/#/CBS/nl/dataset/84732NED/table" },
      { title: "Christmas Island: Australian Bureau of Statistics, 2021 Census QuickStats", url: "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA51710" },
      { title: "Cocos (Keeling) Islands: Australian Bureau of Statistics, 2021 Census QuickStats", url: "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA51860" },
      { title: "Chatham Islands: Stats NZ, 2023 Census place summary (Chatham Islands Territory)", url: "https://tools.summaries.stats.govt.nz/places/TA/chatham-islands-territory" },
      { title: "Chatham Islands pupils (73, all at state schools): Ministry of Education, New Zealand Schools Directory, rolls at 1 October 2026 (Te One 58, Pitt Island 11, Kaingaroa 4)", url: "https://www.educationcounts.govt.nz/directories/list-of-nz-schools" },
      { title: "Tokelau: Tokelau 2015/16 Household Income and Expenditure Survey, poverty analysis (Tokelau National Statistics Office, Stats NZ and the Pacific Community)", url: "https://spccfpstore1.blob.core.windows.net/digitallibrary-docs/files/73/73d325a34d612e880335fea49896211f.pdf" },
      { title: "Gibraltar pupils: Gibraltar Health Authority, Joint Strategic Needs Assessment, education (pupils in government schools, September 2023)", url: "https://www.gha.gi/jsna-education/" },
      { title: "Svalbard population: Statistics Norway, table 07430 (all settlements, second half of 2026)", url: "https://www.ssb.no/statbank/table/07430/" },
      { title: "Svalbard unemployment (estimate): NAV, Hovedtall om arbeidsmarkedet, January and July 2025 (fully unemployed, Svalbard and other areas); people in work: Statistics Norway, Samfunnsforhold på Svalbard (Rapporter 2023/36)", url: "https://www.ssb.no/virksomheter-foretak-og-regnskap/virksomheter-og-foretak/artikler/samfunnsforhold-pa-svalbard" },
      { title: "Pitcairn: Pitcairn Island Economic Review (Solomon Leonard, for the UK government, January 2014)", url: "https://static1.squarespace.com/static/6526ff6fef608a3828c13d05/t/65600116a332be611d46c884/1700790554810/Pitcairn+Islands+Economic+Report+-+Final+Report.pdf" },
      { title: "Borders of the places Natural Earth doesn't list on their own (Caribbean Netherlands, Christmas Island, Cocos, Gibraltar, Svalbard, Pitcairn, Tokelau): Eurostat GISCO countries 2024, 1:1 million; the Chatham Islands: Natural Earth admin-1", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units/countries" }
    ],
    note: "Many of these figures are old (some Factbook poverty rates are from surveys more than ten years old); each row's “Poverty measure” names the source and year. Locales are estimates from population over land area. Built by data-prep/build_islands.py."
  },
  {
    only: "Switzerland",
    group: "Switzerland: cantons, child social assistance and pupils",
    items: [
      { title: "Child poverty: Federal Statistical Office (BFS), social assistance recipients by canton and age (px-x-1304030000_121), social assistance rate for ages 0–17, 2025", url: "https://www.pxweb.bfs.admin.ch/pxweb/de/px-x-1304030000_121/" },
      { title: "Pupils: BFS, compulsory school pupils by school canton (px-x-1502010100_101), 2024/25", url: "https://www.pxweb.bfs.admin.ch/pxweb/de/px-x-1502010100_101/" },
      { title: "Meetings (stand-in): cantonal parliaments' and cantons' YouTube channels (in the “Meetings source” column), checked by hand; regioTVplus and swissbroadcast for Basel-Landschaft and Schaffhausen", url: "https://www.youtube.com/" },
      { title: "Borders: Natural Earth 1:10m admin-1 states and provinces", url: "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/" }
    ],
    note: "Children 0–17 are worked out from the number on social assistance and the rate. Locales are estimates. Built by data-prep/build_switzerland.py."
  },
  {
    only: "Chile",
    group: "Chile: comunas, poverty and enrollment",
    items: [
      { title: "Income poverty by comuna: Ministerio de Desarrollo Social y Familia, small-area estimates (SAE) 2024", url: "https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-2024" },
      { title: "Multidimensional poverty by comuna: the same small-area estimates, 2024", url: "https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-2024" },
      { title: "Enrollment: Mineduc, Resumen de Matrícula por Establecimiento Educacional 2026 (added up by comuna; COD_DEPE gives who runs each school)", url: "https://datosabiertos.mineduc.cl/resumen-de-matricula-por-establecimiento-educacional/" },
      { title: "Borders: geoBoundaries (gbOpen) Chile ADM3, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each municipality's or council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Comunas are matched to borders by name; Pozo Almonte has no border in the file."
  },
  {
    only: "Colombia",
    group: "Colombia: municipalities, poverty and enrollment",
    items: [
      { title: "Multidimensional poverty by municipality: DANE, Medida de pobreza multidimensional de fuente censal (2018 census)", url: "https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/pobreza-y-desigualdad/medida-de-pobreza-multidimensional-de-fuente-censal" },
      { title: "Enrollment and the education authority: Ministry of Education statistics by municipality, 2024 (datos.gov.co, nudc-7mev): gross coverage (cobertura bruta) times the population aged 5–16 gives back the ministry's enrollment count", url: "https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR-B-SICA-Y-MEDIA_POR_MUNICIPIO/nudc-7mev" },
      { title: "Public-school share: Ministry of Education, establecimientos educativos de preescolar, básica y media, 2025 (datos.gov.co, cfw5-qzt5): pupils at official (sector oficial) against non-official schools in each municipality", url: "https://www.datos.gov.co/d/cfw5-qzt5" },
      { title: "Borders: geoBoundaries (gbOpen) Colombia ADM1 and ADM2, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each council's or municipality's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Municipalities are matched to borders by name within their department (found from where each border lies). Barranquilla, Colosó, Providencia and Puerto Santander have no border in the file."
  },
  {
    only: "Brazil",
    group: "Brazil: municipalities, poverty and enrollment",
    items: [
      { title: "Border of Boa Esperança do Norte (created 2025): IBGE, Malha Municipal 2025, Mato Grosso", url: "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/MT/" },
      { title: "Poverty: IBGE, Censo Demográfico 2022, table 10296 (residents by household income per person, in minimum wages), via SIDRA", url: "https://sidra.ibge.gov.br/tabela/10296" },
      { title: "Bolsa Família families by municipality, September 2025: Portal da Transparência (Novo Bolsa Família, pagamentos)", url: "https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia/202509" },
      { title: "Municipal codes (SIAFI to IBGE): Tesouro Nacional, Tabela de Municípios", url: "https://www.tesourotransparente.gov.br/ckan/dataset/lista-de-municipios-do-siafi" },
      { title: "Population: IBGE, Estimativas da População 2025", url: "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2025/estimativa_dou_2025.xls" },
      { title: "Households: IBGE, Censo Demográfico 2022, table 4712, via SIDRA", url: "https://sidra.ibge.gov.br/tabela/4712" },
      { title: "Enrollment: INEP, Sinopse Estatística da Educação Básica 2025 (Censo Escolar), table 1.1, pupils in ensino fundamental and ensino médio in schools in each municipality, all networks", url: "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica" },
      { title: "Public school share: INEP, Sinopse Estatística da Educação Básica 2025 (Censo Escolar), table 1.2, pupils in all of basic education by dependência administrativa in each municipality; public = federal, state and municipal networks, private = the rede privada (including community, religious and philanthropic schools)", url: "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica" },
      { title: "Children 6–17 (and the earlier enrollment count, residents aged 6–17 attending school): IBGE, Censo Demográfico 2022, tables 10058 (people 6–17 attending school) and 9514 (population by age), via SIDRA", url: "https://sidra.ibge.gov.br/tabela/10058" },
      { title: "Borders: geoBoundaries (gbOpen) Brazil ADM1 and ADM2, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each chamber's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Municipalities are matched to borders by name within their state."
  },
  {
    only: "Spain",
    group: "Spain: municipalities, child poverty and population",
    items: [
      { title: "Child poverty: INE, Atlas de Distribución de Renta de los Hogares (ADRH), relative poverty thresholds by sex and age group (one table per province), people under 18 below 60% of the median income per consumption unit, 2019–2024", url: "https://www.ine.es/dynt3/inebase/index.htm?padre=12385&capsel=12384" },
      { title: "Population and share under 18: INE, ADRH demographic indicators (one table per province), 2024", url: "https://www.ine.es/dynt3/inebase/index.htm?padre=12385&capsel=12384" },
      { title: "Estimate for small municipalities without a child figure: the same INE measure for their province's smaller municipalities (under 10,000 people) that have one, weighted by their children (Eurostat's regional rate, ilc_li41, is kept as a fallback but no province needs it)", url: "https://ec.europa.eu/eurostat/databrowser/view/ilc_li41/default/table" },
      { title: "Borders: geoBoundaries (gbOpen) Spain ADM2 (provinces) and ADM3 (municipalities), simplified further with mapshaper", url: "https://www.geoboundaries.org/" },
      { title: "Borders of the 8 municipalities created since 2014 (El Palmar de Troya, Fornes, Fuente Carreteros, La Guijarrosa, La Zarza-Perrunal, San Martín del Tesorillo, Torrenueva Costa, Usansolo): IGN, INSPIRE administrative units service, checked to lie inside the town each was split from", url: "https://www.ign.es/wfs-inspire/unidades-administrativas?service=WFS&request=GetCapabilities" },
      { title: "Meetings (stand-in): each town council's YouTube channel (in the “Meetings source” column), searched for municipalities of 5,000+ people", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Municipalities are matched to borders by name within their province (either form of a two-language name)."
  },
  {
    only: "Peru",
    group: "Peru: districts, poverty and population",
    items: [
      { title: "Poverty and population: INEI, Mapa de pobreza monetaria provincial y distrital 2018, Anexo 1 (95% confidence interval of the monetary poverty rate and 2018 population by district)", url: "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1718/Libro.pdf" },
      { title: "Borders: district boundaries (INEI), as GeoJSON by Juan Eladio Sánchez Rosas (peru-geojson)", url: "https://github.com/juaneladio/peru-geojson" },
      { title: "Borders of the 48 districts created since: Instituto Geográfico Nacional, via OCHA and geoBoundaries (gbHumanitarian PER ADM3), checked to lie inside the district each was made from", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each council's YouTube channel, checked by hand (in the “Meetings source” column)", url: "https://www.youtube.com/" },
      { title: "Enrollment: Ministerio de Educación (MINEDU), ESCALE – Estadística de la Calidad Educativa, Padrón de Instituciones Educativas: pupils (Alumnos) in each school and programme from the Censo Educativo 2025, with its location code (ubigeo), summed by district. Public schools: Tipo de Gestión “Pública de gestión directa” or “Pública de gestión privada”; the rest private", url: "https://escale.minedu.gob.pe/padron-de-iiee" }
    ],
    note: "Built by data-prep/build_latam.py. Districts are matched to borders, and schools to districts, by their INEI code (ubigeo); 50 have no border in the file. ESCALE's enrollment export was downloaded by the project's owner (the site blocks automated downloads) and is kept summed by district in data-prep/inputs/peru/pe_alumnos_2025.json."
  },
  {
    only: "France",
    group: "France: communes, poverty, population and pupils",
    items: [
      { title: "Population of Mayotte's 17 communes: INSEE legal populations from the 2017 census of Mayotte (its latest full census), via the government's geo API; used for their density and estimated locale", url: "https://geo.api.gouv.fr/communes?codeDepartement=976&fields=nom,code,population,surface" },
      { title: "Poverty: INSEE, Filosofi 2023, poverty rate (60% of the median standard of living) and median standard of living by commune and département (dataset DS_FILOSOFI_CC)", url: "https://api.insee.fr/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR" },
      { title: "Child poverty by département: INSEE, Filosofi 2023, poverty rate by age group (dataset DS_FILOSOFI_SAGE_LOG_TP_NIVVIE)", url: "https://api.insee.fr/melodi/file/DS_FILOSOFI_SAGE_LOG_TP_NIVVIE/DS_FILOSOFI_SAGE_LOG_TP_NIVVIE_2023_CSV_FR" },
      { title: "Overseas départements' poverty rates (Guadeloupe, Martinique, French Guiana, Mayotte): INSEE, Revenus et patrimoine des ménages, édition 2024, fiche 1.21 (Filosofi 2021 and the 2017 Budget de famille survey)", url: "https://www.insee.fr/fr/statistiques/fichier/7941411/RPM2024-F21.pdf" },
      { title: "Population: INSEE, populations de référence 2023 (municipal population)", url: "https://api.insee.fr/melodi/file/DS_POPULATIONS_REFERENCE/DS_POPULATIONS_REFERENCE_2023_CSV_FR" },
      { title: "Pupils: Ministry of Education, pupils in nursery and primary schools by school, rentrée 2025 (fr-en-ecoles-effectifs-nb_classes), placed in communes with the school directory (fr-en-annuaire-education)", url: "https://data.education.gouv.fr/explore/dataset/fr-en-ecoles-effectifs-nb_classes/" },
      { title: "Borders: communes and départements (simplified), france-geojson by Grégoire David, simplified further with mapshaper", url: "https://github.com/gregoiredavid/france-geojson" },
      { title: "Borders of 47 communes formed by recent mergers: the French government's geographic API (geo.api.gouv.fr)", url: "https://geo.api.gouv.fr/" },
      { title: "Meetings (stand-in): each town council's YouTube channel (in the “Meetings source” column), searched for communes of 2,000+ people", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Communes are matched to borders by their INSEE code. The border file predates some mergers, which left 492 former communes with no current code; each was placed in the commune it lies in today with geo.api.gouv.fr and drawn as part of it."
  },
  {
    only: "Italy",
    group: "Italy: comuni, incomes, population and pupils",
    items: [
      { title: "Low incomes (stand-in for poverty): Ministry of Economy and Finance, income tax returns (IRPEF) by comune, tax year 2023: filers with a total income of 10,000 euros or less", url: "https://www1.finanze.gov.it/finanze/analisi_stat/public/index.php?opendata=yes" },
      { title: "Comuni, regions and provinces: ISTAT, Elenco dei comuni italiani", url: "https://www.istat.it/classificazione/codici-dei-comuni-delle-province-e-delle-regioni/" },
      { title: "Pupils: Ministry of Education open data, 2024-25, pupils by state school (ALUCORSOETASTA) and by publicly recognised private school (ALUCORSOINDCLAPAR), placed in comuni with the school directories", url: "https://dati.istruzione.it/opendata/opendata/catalogo/" },
      { title: "Borders, population and density: Eurostat GISCO Local Administrative Units (LAU) 2024, simplified with mapshaper", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings (stand-in): each town council's YouTube channel (in the “Meetings source” column), searched for comuni of 3,000+ people", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_italy.py and data-prep/build_latam.py. Comuni are matched to borders and figures by their ISTAT code."
  },
  {
    only: "Poland",
    group: "Poland: gminy, low income and pupils",
    items: [
      { title: "Children on family benefit: Statistics Poland, Local Data Bank (BDL), variable 259889: share of children aged 0-17 whose parents receive the family benefit, 2024", url: "https://bdl.stat.gov.pl/bdl/start" },
      { title: "Social assistance: Statistics Poland, Local Data Bank (BDL), variable 1548717: beneficiaries of community social assistance per 10,000 people, 2024", url: "https://bdl.stat.gov.pl/bdl/start" },
      { title: "Borders, population and density: Eurostat GISCO Local Administrative Units (LAU) 2024, simplified with mapshaper", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Pupils: Ministry of National Education, SIO, “Uczniowie szkół w roku 2025”: pupils by school, 2025/26, summed by gmina (dane.gov.pl, “Dane jednostkowe przedszkoli, szkół i placówek oświatowych”)", url: "https://dane.gov.pl/pl/dataset/288" },
      { title: "Meetings: each council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py (pupils: data-prep/prep_poland_pupils.py). Gminy are matched to borders by their Statistics Poland unit code."
  },
  {
    only: "Japan",
    group: "Japan: municipalities, welfare, pupils and boards of education",
    items: [
      { title: "Public-school share: School Basic Survey (学校基本調査) 2025, municipal tables (市町村別集計) on e-Stat: pupils at elementary, lower secondary and compulsory 9-year schools, all and private, by municipality (released 26 December 2025). Public = all minus private (national schools count as public); the 2025 share is applied to the 2024 enrollment; designated cities' wards are summed. Accessed through the e-Stat API; this service uses the e-Stat API but its content is not guaranteed by the government", url: "https://www.e-stat.go.jp/stat-search/files?toukei=00400001&tstat=000001011528" },
      { title: "Welfare rate: Ministry of Health, Labour and Welfare, 被保護者調査 (survey of welfare recipients), FY2024 final figures, table 8 (2-2), by prefecture, designated city and core city", url: "https://www.e-stat.go.jp/stat-search/files?toukei=00450312" },
      { title: "Population, children under 15, area, pupils and unemployment: Statistics Bureau, 統計でみる市区町村のすがた 2026 (municipal basic data; 2020 census and 2024 school survey)", url: "https://www.e-stat.go.jp/stat-search/files?toukei=00200502" },
      { title: "Borders: Ministry of Land, Infrastructure, Transport and Tourism, 国土数値情報 administrative areas (N03, 2021), as simplified by smartnews-smri/japan-topography", url: "https://github.com/smartnews-smri/japan-topography" },
      { title: "Municipal websites: Wikidata (official website, P856, by local government code, P429)", url: "https://www.wikidata.org/" },
      { title: "Meetings: each board of education's minutes or meeting pages (in the “Meetings source” column)", url: "https://www.e-stat.go.jp/" }
    ],
    note: "Built by data-prep/prep_japan.py and data-prep/build_latam.py. Municipalities are matched to borders and figures by their local government code; designated cities' wards are merged into their city."
  },
  {
    only: "Portugal",
    group: "Portugal: municipalities, minimum income and population",
    items: [
      { title: "Minimum income (stand-in): INE, social insertion income (RSI) beneficiaries per 1,000 people of working age (indicator 0013420), 2025", url: "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0013420&lang=PT" },
      { title: "Family benefit: INE, children and young people receiving the abono de família (indicator 0010284), 2022", url: "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0010284&lang=PT" },
      { title: "Median income: INE, median gross declared income per taxpayer (indicator 0012749), 2024", url: "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0012749&lang=PT" },
      { title: "Population by age: INE, annual population estimates (indicator 0008273), 2023", url: "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008273&lang=PT" },
      { title: "Pupils: DGEEC, Regiões em Números 2024/2025 - Educação, pupils by municipality (one workbook per municipality in each region's volume)", url: "https://www.dgeec.medu.pt/art/educacao-pre-escolar-basico-e-secundario/estatisticas/regioes/652d13f3121f641a986cc632" },
      { title: "Borders: Eurostat GISCO Local Administrative Units (LAU) 2024 (parishes), merged into municipalities with mapshaper", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings (stand-in): each municipality's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_portugal.py and data-prep/build_latam.py. Municipalities are matched by their code (DTMN)."
  },
  {
    only: "Belgium",
    group: "Belgium: municipalities, integration income, income and population",
    items: [
      { title: "Integration income (stand-in): PPS Social Integration, revenu d'intégration / leefloon beneficiaries by municipality, 2025 (stat.mi-is.be)", url: "https://stat.mi-is.be/fr/dashboard/ris_cities?menu=map" },
      { title: "Income: Statbel, fiscal statistics on income by municipality (TF_PSNL_INC_TAX_MUNTY), 2023", url: "https://statbel.fgov.be/en/open-data/fiscal-statistics-income" },
      { title: "Population and children under 18: Statbel, population by place of residence and age (TF_SOC_POP_STRUCT_2025)", url: "https://statbel.fgov.be/en/open-data" },
      { title: "Municipality codes and names: Statbel, REFNIS code list (1 January 2025)", url: "https://statbel.fgov.be/en/open-data/code-refnis-0" },
      { title: "Pupils, Flanders: Flemish education department, Dataloep enrolments by school site, 1 February 2025 (nursery and primary, ordinary and special); public-school share from the same file: pupils at schools run by a municipality, a province, the Flemish community (GO!) or the VGC in Brussels. “Free” schools (mostly Catholic) are publicly funded but privately run, so they count as private, as in the Netherlands and Spain. Brussels and Wallonia have no public-school figure: no split by school network was found for French-speaking schools", url: "https://opendata.dataplatform-onderwijs.vlaanderen.be/dataloep/inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1feb.csv" },
      { title: "Pupils, Wallonia and the German-speaking municipalities: IWEPS WalStat, pupils enrolled in nursery and primary schools by municipality, 2024", url: "https://www.odwb.be/explore/dataset/243300/" },
      { title: "Pupils, Brussels: IBSA, origin and destination of pupils by municipality (tables 6.3.2.2 and 6.3.2.3), 2023-24", url: "https://ibsa.brussels/themes/enseignement/origine-destination-des-eleves" },
      { title: "Borders: Eurostat GISCO Local Administrative Units (LAU) 2024, merged into the 2025 municipalities with mapshaper", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings: each municipality's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_belgium.py and data-prep/build_latam.py. Municipalities are matched by their REFNIS code; the 2025 mergers are in data-prep/inputs/belgium/be_mergers_2025.json."
  },
  {
    only: "Australia",
    group: "Australia: council areas, income support and the census",
    items: [
      { title: "Cue (WA): enrollment of Cue Primary School, the shire's only school (no private school), from the WA Department of Education's Schools Online, used because the census figure is suppressed", url: "https://www.det.wa.edu.au/schoolsonline/student_current.do?schoolID=5127&pageID=SP01" },
      { title: "Sandstone (WA): no school since 2013 and no school-age residents; a child living there would study remotely (Shire of Sandstone)", url: "https://www.sandstone.wa.gov.au/council/facilities/education" },
      { title: "Sandstone: 2021 Census QuickStats (ABS)", url: "https://abs.gov.au/census/find-census-data/quickstats/2021/SAL51326" },
      { title: "Wikipedia: list of schools in rural Western Australia (Sandstone's school, closed in 2013; Cue Primary School)", url: "https://en.wikipedia.org/wiki/List_of_schools_in_rural_Western_Australia" },
      { title: "Income support (stand-in): Department of Social Services, DSS Benefit and Payment Recipient Demographics, June 2026, by local government area (data.gov.au)", url: "https://data.gov.au/data/dataset/dss-payment-demographic-data" },
      { title: "Population, age, median family income and school attendance: Australian Bureau of Statistics, 2021 Census General Community Profile DataPack, local government areas (tables G01, G02, G04 and G15)", url: "https://www.abs.gov.au/census/find-census-data/datapacks" },
      { title: "Borders: Australian Bureau of Statistics, ASGS Edition 3 local government areas 2021, simplified with mapshaper", url: "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files" },
      { title: "Meetings (stand-in): each council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_australia.py and data-prep/build_latam.py. Council areas are matched by their 2021 LGA code (Merri-bek by its old code, as Moreland)."
  },
  {
    only: "Croatia",
    group: "Croatia: cities and municipalities, poverty map",
    items: [
      { title: "Poverty: World Bank and Croatian Bureau of Statistics, Croatia small-area estimation of consumption-based poverty (poverty maps), October 2016, 2011 data; city, municipal and county tables", url: "https://www.worldbank.org/en/country/croatia/publication/croatia-poverty-maps" },
      { title: "The poverty map online (Croatian Bureau of Statistics, Geostat)", url: "https://geostat.dzs.hr/?lang=en" },
      { title: "Borders and population: Eurostat GISCO Local Administrative Units (LAU) 2024; counties: GISCO NUTS 3 (2024)", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings: each council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" },
      { title: "Public-school share: Ministry of Science, Education and Youth, list of primary schools with their founder (osnivač), May 2025. Places with no school founded by an association, church body, company or person are 100% public; the 12 places with one (Zagreb, Split, Rijeka, Osijek, Zadar, Šibenik, Varaždin, Požega, Virovitica, Novska, Samobor, Dugopolje) have no figure, as the list counts schools, not pupils", url: "https://data.gov.hr/ckan/dataset/2841fb78-c828-4ab2-8cdc-f22abeed3a8c" }
    ],
    note: "Built by data-prep/prep_croatia.py and data-prep/build_latam.py. Places are matched to the poverty map by name (shared names by the map's qualifier or population) and placed in counties by their borders."
  },
  {
    only: "Argentina",
    group: "Argentina: provinces",
    items: [
      { title: "Poverty: INDEC, Encuesta Permanente de Hogares, “Incidencia de la pobreza y la indigencia en 31 aglomerados urbanos”, first half of 2026: cuadros (Cuadro 4.1 and “Poblaciones”, people below the poverty line by urban area; Cuadros 3.2 and 3.4, by age)", url: "https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-46-152" },
      { title: "Population and land area: INDEC, Censo Nacional de Población, Hogares y Viviendas 2022, final results, Cuadro 2 (population and density by jurisdiction, 2010 and 2022)", url: "https://www.indec.gob.ar/ftp/cuadros/poblacion/c2022_tp_est_c2.xlsx" },
      { title: "Pupils and public-school share: Ministry of Education (Secretaría de Educación), Relevamiento Anual 2024, pupils by department, management sector and grade (“Base de Datos por Escuela 2024”), datos.gob.ar", url: "https://datos.gob.ar/dataset/educacion-base-datos-por-escuela-2024" },
      { title: "Borders: geoBoundaries (gbOpen) ARG ADM1 and ADM2, simplified; Entre Ríos rebuilt from its 17 departments (ADM2), as the ADM1 file draws it inside Buenos Aires province", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each provincial legislature's YouTube channel (in the “Meetings source” column), searched November 2026; dates from the videos' titles", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_argentina.py and data-prep/build_latam.py (argentina). Two surveyed urban areas straddle a provincial border (San Nicolás – Villa Constitución, Viedma – Carmen de Patagones); each is counted in the province of its larger part. The ministry's pupil file (downloaded by hand, as its link needs a Microsoft sign-in for automated tools) is added up by province; departments it masks for small counts still count toward their province."
  },
  {
    only: "Israel",
    group: "Israel: local authorities",
    items: [
      { title: "Local authorities: Interior Ministry, list of local authorities (municipalities, local councils and regional councils), data.gov.il", url: "https://data.gov.il/" },
      { title: "Poverty stand-in: Ministry of Welfare and Social Affairs, people and cases known to the social services departments by local authority, 2010–2019 (2019 used), data.gov.il", url: "https://data.gov.il/" },
      { title: "Residents: Central Bureau of Statistics, Census 2022, population and households by locality, data.gov.il (added up over a regional council's localities)", url: "https://data.gov.il/dataset/3bd97fde-6cc3-456d-ab63-1caad16b2b6a" },
      { title: "Children under 18 (estimated from ages 0–5 and 6–18) and a few populations: Population and Immigration Authority, residents in Israel by locality and age groups, data.gov.il", url: "https://data.gov.il/dataset/00172ee8-4433-4d5d-8fd4-11f0f08ce5c4" },
      { title: "Localities' regional council and subdistrict: Population and Immigration Authority, list of localities in Israel, data.gov.il", url: "https://data.gov.il/dataset/3fc54b81-25b3-4ac7-87db-248c3e1602de" },
      { title: "Socio-economic cluster: Central Bureau of Statistics, characterization and classification of local authorities by socio-economic level, 2019", url: "https://www.cbs.gov.il/" },
      { title: "Pupils and public-school share: Ministry of Education, characteristics of education institutions (pupils per school, with its legal status), 2015, data.gov.il", url: "https://data.gov.il/dataset/mosdot" },
      { title: "Borders: © OpenStreetMap contributors (ODbL), administrative boundaries (admin_level 8), from Geofabrik's Israel and Palestine extract", url: "https://download.geofabrik.de/asia/israel-and-palestine.html" },
      { title: "Meetings: each local authority's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_israel.py and data-prep/build_latam.py (israel). Sources are matched by the authority's name (a few by hand); districts come from the localities' subdistricts. Modi'in Illit and Sha'ar Shomron (formed in 2024) have no border in OpenStreetMap, and two industrial local councils (Migdal Tefen, Neot Hovav) have no residents."
  },
  {
    only: "Slovenia",
    group: "Slovenia: municipalities",
    items: [
      { title: "Poverty stand-in: Statistical Office of the Republic of Slovenia (SURS), 0883206S, net income by source, average per capita, by municipality, 2024 (“Parental, family and social benefits” over “Net income - TOTAL”)", url: "https://pxweb.stat.si/SiStatData/pxweb/en/Data/-/0883206S.px" },
      { title: "Population, area and pupils (basic-school pupils by the school's municipality; upper-secondary pupils by residence): SURS, 2640010S, selected data on municipalities, 2025–2026", url: "https://pxweb.stat.si/SiStatData/pxweb/en/Data/-/2640010S.px" },
      { title: "Children under 18: SURS, 05C4006S, population by age group and sex, municipalities, latest half-year", url: "https://pxweb.stat.si/SiStatData/pxweb/en/Data/-/05C4006S.px" },
      { title: "Borders: geoBoundaries (gbOpen) SVN ADM2, simplified, matched to SURS names", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each municipal council's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_slovenia.py and data-prep/build_latam.py (slovenia). geoBoundaries spells some names without their diacritics, so borders are matched exactly where possible, then by closest name (all 212 checked)."
  },
  {
    only: "Taiwan",
    group: "Taiwan: counties and cities",
    items: [
      { title: "Poverty stand-in: Ministry of Health and Welfare, Department of Statistics, low-income households and persons by county and city (table 1.1.1, with persons as a share of the population it uses), 2026 Q2", url: "https://www.mohw.gov.tw/dl-27850-056a753c-fbce-4fff-a373-530accaf6572.html" },
      { title: "Poverty stand-in: Ministry of Health and Welfare, Department of Statistics, middle-low-income households and persons by county and city (table 1.1.5), 2026 Q2", url: "https://www.mohw.gov.tw/dl-22058-0e1cd81e-d145-45ef-8ee8-43fbb074c2b8.html" },
      { title: "Pupils and public-school share: Ministry of Education, Department of Statistics open data, school year 2025/26: elementary schools (edu_B_3_2), junior high schools (edu_B_3_8) and senior high schools (edu_B_4_2) by county and city", url: "https://stats.moe.gov.tw/files/opendata/edu_B_3_2.csv" },
      { title: "Borders: geoBoundaries (gbOpen) TWN ADM1, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each county or city council's YouTube channel (in the “Meetings source” column), searched November 2026; dates from the videos' titles (Republic of China years converted)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_taiwan.py and data-prep/build_latam.py (taiwan). Two civic channels that comment on council proceedings are left out; titles with no date count only when they name a numbered session or an agenda."
  },
  {
    only: "Uruguay",
    group: "Uruguay: departments",
    items: [
      { title: "Poverty stand-in: Ministry of Social Development (MIDES), Tarjeta Uruguay Social cards by type and department, 2024, in INE's Anuario Estadístico Nacional 2025, table 3.9.3", url: "https://www5.ine.gub.uy/documents/ANUARIOS/Anuario%202025/3%20-%20ASPECTOS%20SOCIALES/3.9%20Desarrollo%20Social/3.9.3ok.xlsx" },
      { title: "Poverty bands and national rates: INE, Estimación de la pobreza por el método del ingreso, año 2025 (map 1, households below the poverty line by department; tables 1–3)", url: "https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/HTML/ECH/Pobreza/2025/Informe%20pobreza%20Anual-2025.html" },
      { title: "Population: INE, Anuario Estadístico Nacional 2025, table 2.2.4, population projected to 30 June by department", url: "https://www5.ine.gub.uy/documents/ANUARIOS/Anuario%202025/2%20-%20POBLACI%C3%93N/2.2%20Proyecciones/2.2.4.xls" },
      { title: "Pupils and public-school share: INE, Anuario Estadístico Nacional 2025, tables 3.1.3 (common primary education), 3.1.6 (lower secondary) and 3.1.10 (upper secondary), 2024, by department and form of administration", url: "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102" },
      { title: "Borders: geoBoundaries (gbOpen) URY ADM1, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each Junta Departamental's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_uruguay.py and data-prep/build_latam.py (uruguay). The yearbook's TUS table has Río Negro and Rivera swapped in its 2023 column; the 2024 figures used here match its historical series."
  },
  {
    only: "Costa Rica",
    group: "Costa Rica: cantons",
    items: [
      { title: "Poverty stand-in: UNDP Costa Rica, Atlas de Desarrollo Humano Cantonal 2024, report 2, Cuadro 5, cantons ordered by the Multidimensional Poverty Index (IPM), 2023", url: "https://hdr.undp.org/system/files/documents/national-report-document/atlas-cantonal-reporte-2.pdf" },
      { title: "Population and area: Spanish Wikipedia, “Anexo:Cantones de Costa Rica” (INEC's 2022 estimate from the census's partial results; INEC's own site refuses automated downloads)", url: "https://es.wikipedia.org/wiki/Anexo:Cantones_de_Costa_Rica" },
      { title: "Pupils and public-school share: Ministry of Public Education (MEP), Departamento de Análisis Estadístico, initial enrollment by school, 2014–2022 (2022 used): day primary schools (grades 1–6) and secondary schools (grades 7–12)", url: "https://www.mep.go.cr/acerca-del-mep/analisis-estadistico/estadisticas-educativas" },
      { title: "Borders: geoBoundaries (gbOpen) CRI ADM2, simplified (Monteverde not yet separate)", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each municipality's YouTube channel (in the “Meetings source” column), searched November 2026; some titles shown machine-translated into English by YouTube are matched too", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_costa_rica.py and data-prep/build_latam.py (costa_rica). MEP's 2022 files predate Puerto Jiménez's separation from Golfito and list Monteverde under Puntarenas, so schools in those districts are counted toward the new cantons; Sarchí appears under its former name, Valverde Vega. The Municipality of Puerto Jiménez's channel was found for Jiménez (Cartago) and is moved to Puerto Jiménez."
  },
  {
    only: "Lithuania",
    group: "Lithuania: municipalities",
    items: [
      { title: "Poverty: Official Statistics Portal (Statistics Lithuania), S3R453_M3080308, at-risk-of-poverty rate by municipality, 2026", url: "https://osp.stat.gov.lt/" },
      { title: "Social assistance recipients per 1,000 residents (S3R0243_M3160702, 2025) and pupils receiving free school meals (S3R358_M3160909_1, 2025): Official Statistics Portal", url: "https://osp.stat.gov.lt/" },
      { title: "Pupils: Official Statistics Portal, S3R057_M3110302_3, general school pupils by municipality, 2025/26", url: "https://osp.stat.gov.lt/" },
      { title: "Population and children 0–15: Official Statistics Portal, S3R167_M3010213, residents at the start of 2026 by municipality and age", url: "https://osp.stat.gov.lt/" },
      { title: "Data API: osp-rs.stat.gov.lt (SDMX), dataflows above", url: "https://osp-rs.stat.gov.lt/rest_xml/dataflow/" },
      { title: "English names: English Wikipedia, “Municipalities of Lithuania”", url: "https://en.wikipedia.org/wiki/Municipalities_of_Lithuania" },
      { title: "Borders: geoBoundaries (gbOpen) LTU ADM2, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each municipality's or council's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_lithuania.py and data-prep/build_latam.py (lithuania)."
  },
  {
    only: "South Africa",
    group: "South Africa: municipalities",
    items: [
      { title: "Poverty stand-in, learners and public-school share: Department of Basic Education, EMIS, national masterlist of ordinary schools, 2023 (learners, sector, quintile and local municipality of each school)", url: "https://www.education.gov.za/Programmes/EMIS/EMISDownloads.aspx" },
      { title: "Municipalities, population (Census 2022) and area: English Wikipedia, “List of municipalities in South Africa”", url: "https://en.wikipedia.org/wiki/List_of_municipalities_in_South_Africa" },
      { title: "Borders: geoBoundaries (gbOpen) ZAF ADM3, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each municipality's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_south_africa.py and data-prep/build_latam.py (south_africa). Schools are placed by the local municipality the masterlist gives; renamed or merged municipalities (such as Engcobo, now Dr A.B. Xuma, and Tlokwe and Ventersdorp, now JB Marks) are matched to today's, and about 16,500 learners in schools with no municipality given are left out."
  },
  {
    only: "Kenya",
    group: "Kenya: counties",
    items: [
      { title: "Child poverty (Annex Table E.2) and all-ages poverty (Table 4.4) by county: KNBS, The Kenya Poverty Report 2022 (published 2024)", url: "https://www.knbs.or.ke/wp-content/uploads/2024/10/The-Kenya-Poverty-Report-2022.pdf" },
      { title: "Pupils: KNBS, Statistical Abstract 2025, Tables 15.4a (primary), 15.4b (junior school) and 15.6 (secondary), enrolment by county, 2024 (provisional)", url: "https://www.knbs.or.ke/wp-content/uploads/2025/11/2025-Statistical-Abstract.pdf" },
      { title: "Counties, former provinces, population (2019 census) and area: English Wikipedia, “Counties of Kenya”", url: "https://en.wikipedia.org/wiki/Counties_of_Kenya" },
      { title: "Borders: geoBoundaries (gbOpen) KEN ADM1, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each county assembly's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_kenya.py and data-prep/build_latam.py (kenya). KNBS's site sends an incomplete certificate chain, so the downloads added the intermediate certificate it names (Let's Encrypt) to the trusted set rather than skipping verification."
  },
  {
    only: "Georgia (country)",
    group: "Georgia: municipalities",
    items: [
      { title: "Poverty stand-in: Geostat (from the Social Service Agency), number of families registered in the Targeted Social Assistance database and receiving subsistence allowance, by municipality, end of 2025", url: "https://www.geostat.ge/en/modules/categories/55/social-protection" },
      { title: "Population: Geostat, population as of 1 January 2026 by regions and self-governed units", url: "https://www.geostat.ge/en/modules/categories/41/population" },
      { title: "Pupils: Geostat, number of public and private schools, pupils and teachers by municipalities, 2025/26", url: "https://www.geostat.ge/en/modules/categories/59/general-education" },
      { title: "Georgian names: Georgian Wikipedia, list of municipalities of Georgia", url: "https://ka.wikipedia.org/" },
      { title: "Borders: geoBoundaries (gbOpen) GEO ADM2, simplified (no separate borders for Batumi, Kutaisi, Rustavi and Poti)", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each council's or municipality's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_georgia.py and data-prep/build_latam.py (georgia). The allowance table splits some towns into “City” and “Municipality” rows, which are added together; it has no row for Akhalkalaki."
  },
  {
    only: "South Korea",
    group: "South Korea: cities and provinces",
    items: [
      { title: "Poverty stand-in: Ministry of Health and Welfare, 2025년 국민기초생활보장 수급자 현황 (National Basic Livelihood Security recipients, 2025), Table 1 and the recipient rate by province", url: "https://www.mohw.go.kr/board.es?mid=a10411010100&bid=0019&act=view&list_no=1491455" },
      { title: "Pupils: Ministry of Education and KEDI, 연도별 시도별 현황 (education statistics by city and province, updated 1 October 2026), sheet 01, via the Education Statistics Service and data.go.kr", url: "https://kess.kedi.re.kr/post/6731854?itemCode=04&menuId=m_02_04_03_01" },
      { title: "Borders: geoBoundaries (gbOpen) KOR ADM1, simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each metropolitan or provincial council's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_korea.py and data-prep/build_latam.py (south_korea). Population is the ministry's recipients over its recipient rate, so approximate (it adds up to 51.12 million, against the 51.12 million the ministry uses)."
  },
  {
    only: "India",
    group: "India: districts",
    items: [
      { title: "Poverty: NITI Aayog, National Multidimensional Poverty Index: A Progress Review 2023 (based on NFHS-5, 2019-21), each state's district table and chart of the headcount ratio", url: "https://www.niti.gov.in/sites/default/files/2023-08/India-National-Multidimentional-Poverty-Index-2023.pdf" },
      { title: "Population and states: English Wikipedia, “List of districts in India” (Census 2011)", url: "https://en.wikipedia.org/wiki/List_of_districts_in_India" },
      { title: "Population where the map's border differs from the list's district (Andhra Pradesh before 2022, Chennai, Kancheepuram) and for Phek and Peren: Census of India 2011, Primary Census Abstract", url: "https://censusindia.gov.in/census.website/data/census-tables" },
      { title: "Population where it's higher than the census's, or there's no census figure: WorldPop, India age and gender structures 2025 (R2025A, 1 km), all ages summed over the district's border", url: "https://data.humdata.org/dataset/worldpop-age-and-gender-structures-2015-2030-ind" },
      { title: "Enrollment (estimated): WorldPop, India age and gender structures 2025 (R2025A, 1 km, constrained), via the Humanitarian Data Exchange: children aged 6–17 summed over each district's border", url: "https://data.humdata.org/dataset/worldpop-age-and-gender-structures-2015-2030-ind" },
      { title: "Borders: geoBoundaries (gbOpen) IND ADM1 and ADM2, simplified; districts placed in states by location. Jammu and Kashmir's and Ladakh's districts are clipped to the area India administers (Natural Earth 1:50m, India and the Siachen Glacier)", url: "https://www.geoboundaries.org/" },
      { title: "Meetings: each zila parishad's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_india.py and data-prep/build_latam.py (india). The report's district tables are read from the PDF by position; Bihar's and a few small states' come from their charts. Renamed and respelled districts are matched with a list of aliases; Charki Dadri and Jogulamba Gadwal, newer than the map, have no border of their own, and Warangal Rural and Urban share one (their mean is shown)."
  },
  {
    only: "Latvia",
    group: "Latvia: state cities and municipalities",
    items: [
      { title: "Poverty stand-in: Official Statistics Portal, PPS040, municipal social assistance recipients by type of assistance: children receiving the basic benefits (guaranteed minimum income and housing benefit), 2025", url: "https://data.stat.gov.lv/pxweb/en/OSP_PUB/START__VES__PP__PPS/PPS040/" },
      { title: "Children 0–17 and population: Official Statistics Portal, IRD041, population by age at the start of 2026", url: "https://data.stat.gov.lv/pxweb/en/OSP_PUB/START__POP__IR__IRD/IRD041/" },
      { title: "Pupils and public-school share: Ministry of Education and Science, “Izglītojamo skaits sadalījumā pa vispārējās izglītības programmām”, 1 October 2025 (pupils in grades 1–12 by school, with who runs it), data.gov.lv", url: "https://data.gov.lv/dati/lv/dataset/3ef3dea2-20e6-47ae-addc-2f55d11f7be2" },
      { title: "Borders: Eurostat GISCO Local Administrative Units (LAU) 2024; Varakļāni added to Madona (merged 1 July 2025)", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings: each council's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" },
      { title: "Council sittings must be recorded and published: Local Government Law (Pašvaldību likums), Latvijas Vēstnesis", url: "https://likumi.lv/ta/id/336956-pasvaldibu-likums" }
    ],
    note: "Built by data-prep/prep_baltic.py and data-prep/build_latam.py (latvia). Children in households on the basic benefits are counted over the whole of 2025, so the figure is higher than a monthly count would be."
  },
  {
    only: "Estonia",
    group: "Estonia: municipalities",
    items: [
      { title: "Poverty stand-in: Statistics Estonia, SK410, subsistence benefits by administrative unit: applications granted per 1,000 inhabitants, 2025 (shown per 100 residents in an average month)", url: "https://andmed.stat.ee/en/stat/sotsiaalelu__sotsiaalne-kaitse/SK410" },
      { title: "Population, children 0–17 and the 7–18 ages for the enrollment estimate: Statistics Estonia, RV0240, population by sex, age and place of residence, 1 January 2026", url: "https://andmed.stat.ee/en/stat/rahvastik__rahvastikunaitajad-ja-koosseis__rahvaarv-ja-rahvastiku-koosseis/RV0240" },
      { title: "Borders: Eurostat GISCO Local Administrative Units (LAU) 2024; Toila added to Kohtla-Järve (merged in 2025)", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings: each council's YouTube channel (in the “Meetings source” column), searched November 2026", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_baltic.py and data-prep/build_latam.py (estonia). Kohtla-Järve's 2025 benefit figure adds Toila's applications to its own, over the merged population."
  },
  {
    only: "Philippines",
    group: "Philippines: cities and municipalities, poverty",
    items: [
      { title: "Poverty: Philippine Statistics Authority, Municipal and City Level Small Area Poverty Estimates, 2018 and 2021", url: "https://psa.gov.ph/statistics/poverty-sae/stat-tables" },
      { title: "Poverty, highly urbanized and independent cities: PSA OpenSTAT, table 2a, poverty incidence among population by region, province and highly urbanized city, 2018, 2021 and 2023", url: "https://openstat.psa.gov.ph/" },
      { title: "Population: PSA mid-year population projections by city and municipality, 2020–2025 (via the Humanitarian Data Exchange)", url: "https://data.humdata.org/dataset/philippines-population-projection-2020-2025-admin3" },
      { title: "Borders: faeldon/philippines-json-maps (PSGC 2023), simplified with mapshaper", url: "https://github.com/faeldon/philippines-json-maps" },
      { title: "Meetings: each council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_philippines.py and data-prep/build_latam.py. Places are matched by their PSGC code (the old six-digit code's province and municipality digits), or by name where the code changed."
  },
  {
    only: "Malaysia",
    group: "Malaysia: districts, poverty, population and schools",
    items: [
      { title: "Poverty: Department of Statistics Malaysia (DOSM), Household Income and Expenditure Survey 2024, poverty by district (hh_poverty_district; OpenDOSM)", url: "https://open.dosm.gov.my/data-catalogue/hh_poverty_district" },
      { title: "Household income: DOSM, Household Income and Expenditure Survey 2024, income by district (hies_district; OpenDOSM)", url: "https://open.dosm.gov.my/data-catalogue/hies_district" },
      { title: "Population, all ages and by age: DOSM, population by district, 2025 (population_district; OpenDOSM)", url: "https://open.dosm.gov.my/data-catalogue/population_district" },
      { title: "Enrollment: Ministry of Education, enrolment in government and government-aided schools by district, 2025 (enrolment_school_district; data.gov.my)", url: "https://data.gov.my/data-catalogue/enrolment_school_district" },
      { title: "Borders: DOSM, administrative districts (dosm-malaysia/data-open on GitHub)", url: "https://github.com/dosm-malaysia/data-open" },
      { title: "Meetings (stand-in): each local council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_malaysia.py and data-prep/build_latam.py (malaysia). Education districts that differ from the administrative ones (Kinta Utara and Selatan, Kuala Muda/Yan and others) don't match a district, so those districts' enrollment is an estimate."
  },
  {
    only: "Indonesia",
    group: "Indonesia: regencies and cities, poverty and population",
    items: [
      { title: "Poverty and population: Statistics Indonesia (BPS), 2020, as published in the World Bank's Indonesia Database for Policy and Economic Research (INDO-DAPOER), indicators SI.POV.NAPR.ZS and SP.POP.TOTL", url: "https://databank.worldbank.org/source/indonesia-database-for-policy-and-economic-research" },
      { title: "Enrollment: Ministry of Primary and Secondary Education (Kemendikdasmen), Portal Data, “Jumlah peserta didik menurut agama”, SD/MI and equivalent, 2025, by regency and city (public and private; religions added up)", url: "https://data.kemendikdasmen.go.id/dataset" },
      { title: "Borders: geoBoundaries (gbOpen) IDN ADM2 and ADM1, simplified; provinces by location", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each regional council's (DPRD) YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_indonesia.py and data-prep/build_latam.py (indonesia). Renamed regencies are matched by hand and shown under their current names: Pasir is now Paser, Pontianak regency Mempawah, Mamuju Utara Pasangkayu, Toba Samosir Toba, and Maluku Tenggara Barat Kepulauan Tanimbar."
  },
  {
    only: "Paraguay",
    group: "Paraguay: districts, poverty and population",
    items: [
      { title: "Poverty: Instituto Nacional de Estadística (INE), Mapa de pobreza monetaria distrital 2022, Cuadro 1 (incidence of poverty by district, with its 95% range)", url: "https://www.ine.gov.py/vt/publicacion.php?publicacion=295" },
      { title: "Population: INE, Estimaciones y proyecciones de la población distrital, revisión 2025 (mid-2025)", url: "https://www.ine.gov.py/vt/publicacion.php?publicacion=284" },
      { title: "Enrollment (estimated): WorldPop, Paraguay age and gender structures 2025 (R2025A, 1 km), children aged 6–17 summed over each border", url: "https://data.humdata.org/dataset/worldpop-age-and-gender-structures-2015-2030-pry" },
      { title: "Borders: geoBoundaries (gbOpen) PRY ADM2 and ADM1, simplified; departments by location", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each municipal council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/prep_paraguay.py and data-prep/build_latam.py (paraguay). District names are matched within each department, allowing for spelling differences (“Gral.” and “General”, Guaraní y and i)."
  },
  {
    only: "Ecuador",
    group: "Ecuador: cantons, poverty, population and pupils",
    items: [
      { title: "Poverty: INEC and the World Bank, consumption poverty map by canton (2010 census with the 2013-14 Encuesta de Condiciones de Vida), as published on the Humanitarian Data Exchange by the British Red Cross Maps Team", url: "https://data.humdata.org/dataset/947e78a1-0e3d-4f6f-a956-4d6f80915d84" },
      { title: "National NBI rates for 2001-2022 (2022: 39.8% of people, 49.4% of children): INEC, Pobreza por Necesidades Básicas Insatisfechas, methodology book", url: "https://www.ecuadorencifras.gob.ec/documentos/web-inec/Bibliotecas/Libros/NBI_VersionLibroMetodologico.pdf" },
      { title: "Galápagos poverty rate (about 31% in 2010, measure not stated): BBC News, 2013", url: "https://www.bbc.com/news/world-latin-america-22812108" },
      { title: "Unmet basic needs: INEC, Pobreza por necesidades básicas insatisfechas (NBI), 2010 census, by canton", url: "https://www.ecuadorencifras.gob.ec/pobreza-por-necesidades-basicas-insatisfechas/" },
      { title: "Pupils: Ministry of Education (MINEDUC), Registro Administrativo Histórico 2009-2024, start of the 2024-25 school year, by school", url: "https://www.datosabiertos.gob.ec/dataset/5d1838d2-4efb-44a3-8c36-eebb5a8f798a" },
      { title: "Borders: geoBoundaries (gbOpen) Ecuador ADM1 (provinces) and ADM2 (cantons), simplified further with mapshaper", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each cantonal council's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" },
      { title: "Checked but not used: the 2022 census results site, which refuses automated downloads", url: "https://www.censoecuador.gob.ec/" }
    ],
    note: "Built by data-prep/build_latam.py. Cantons are matched to borders by name within their province."
  },
  {
    only: "Mexico",
    group: "Mexico: municipalities, poverty and enrollment",
    items: [
      { title: "Enrollment: SEP, Dirección General de Planeación, Programación y Estadística Educativa, Principales cifras (Formato 911 school statistics), ciclo 2025-2026, escolarizada, educación básica, by municipality for each state, all schools and public schools (data-prep/prep_mexico_pupils.py)", url: "https://www.planeacion.sep.gob.mx/principalescifras/" },
      { title: "Borders of 6 municipalities created since 2012: INEGI, via the UN and geoBoundaries (gbAuthoritative MEX ADM2), checked to lie inside the municipality each was made from", url: "https://www.geoboundaries.org/" },
      { title: "Borders of 6 more (Coatetelco, Honduras de la Sierra, Hueyapan, San Quintín, Seybaplaya, Xoxocotla): INEGI, Marco Geoestadístico, diciembre de 2025, from its geographic web service (wscatgeo), checked the same way", url: "https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgem/17034" },
      { title: "Poverty by municipality: CONEVAL, Medición de la pobreza municipal 2010–2020 (concentrado de indicadores)", url: "https://www.coneval.org.mx/Medicion/Paginas/Pobreza-municipio-2010-2020.aspx" },
      { title: "Children 6–17, population, and enrollment for the four municipalities SEP can't be matched to (census residents aged 6–17 attending school): INEGI, Censo de Población y Vivienda 2020, Principales resultados por localidad (ITER), municipal totals", url: "https://www.inegi.org.mx/programas/ccpv/2020/#datos_abiertos" },
      { title: "Borders: geoBoundaries (gbOpen) Mexico ADM1 and ADM2 (2012 municipalities), simplified", url: "https://www.geoboundaries.org/" },
      { title: "Meetings (stand-in): each municipality's YouTube channel (in the “Meetings source” column)", url: "https://www.youtube.com/" }
    ],
    note: "Built by data-prep/build_latam.py. Municipalities are matched to borders by name within their state; the 12 created after 2012 have borders of their own from INEGI (above)."
  },
  {
    only: "Iceland",
    group: "Iceland: municipalities, children and council meetings",
    items: [
      { title: "Children 6–15 and population: Statistics Iceland MAN02005 (population by sex, age and municipality, 1 January 2026)", url: "https://px.hagstofa.is/pxis/pxweb/is/Ibuar/Ibuar__mannfjoldi__2_byggdir__sveitarfelog/MAN02005.px" },
      { title: "Enrollment: Statistics Iceland SKO02102 (compulsory school pupils by school, autumn 2025), added up by the municipality each school is in", url: "https://px.hagstofa.is/pxis/pxweb/is/Samfelag/Samfelag__skolamal__2_grunnskolastig__0_gsNemendur/SKO02102.px" },
      { title: "Public and private schools: Statistics Iceland SKO02202, 2025: 13 private compulsory schools with 1,500 pupils, identified by name in SKO02102 (Landakotsskóli, Skóli Ísaks Jónssonar, Tjarnarskóli, Suðurhlíðarskóli, the two Waldorf schools, Arnarskóli, Alþjóðaskólinn á Íslandi, NÚ, the Hjallastefnan schools and Ásgarður)", url: "https://px.hagstofa.is/pxis/pxweb/is/Samfelag/Samfelag__skolamal__2_grunnskolastig__2_gsSkolahald/SKO02202.px" },
      { title: "Child low income (national): Eurostat ilc_li02, children under 18 below 60% of the median income, 2020", url: "https://ec.europa.eu/eurostat/databrowser/view/ilc_li02/default/table" },
      { title: "Checked but not used: Statistics Iceland LIF01140, child low income by residence (its “total” row is higher than both the capital area and the rest of the country)", url: "https://px.hagstofa.is/pxis/pxweb/is/Samfelag/Samfelag__lifskjor__3_fjarhagsstada__1_einstaklingar/LIF01140.px" },
      { title: "Borders: Eurostat GISCO LAU 2023 (names taken from Statistics Iceland's municipality codes, since eight LAU names are wrong)", url: "https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units" },
      { title: "Meetings: each municipality's own YouTube channel (in the “Meetings source” column); videos of council meetings, one per meeting", url: "https://www.youtube.com/" }
    ],
    note: "Locales are estimates from population over area. Skagabyggð and Tálknafjarðarhreppur merged into Húnabyggð and Vesturbyggð in 2024 and are drawn as part of them. Built by data-prep/build_iceland.py."
  },
  {
    only: "Ireland",
    group: "Ireland: Education and Training Boards, unemployment and children",
    items: [
      { title: "ETB areas: Education and Training Boards Act 2013, Schedule 1 (each ETB's local authority areas)", url: "https://www.irishstatutebook.ie/eli/2013/act/11/schedule/1/enacted/en/html" },
      { title: "Poverty: Eurostat ilc_li41, at-risk-of-poverty rate by NUTS 2 region (Northern and Western, Southern, Eastern and Midland), 2025", url: "https://ec.europa.eu/eurostat/databrowser/view/ilc_li41/default/table" },
      { title: "Unemployment: CSO Census 2022, SAP2022T8T1LEA22, population aged 15 and over by principal economic status (local electoral areas, added up by council area)", url: "https://data.gov.ie/dataset/sap2022t8t1lea22-population-aged-15-years-and-over-by-principal-economic-status-and-sex" },
      { title: "Children 5–17 and council borders: CSO Census 2022 Census Hub, Table 1.1 by local authority", url: "https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/arcgis/rest/services/CensusHub2022_T1_1_LA/FeatureServer" },
      { title: "Meetings: the ETBs' YouTube channels (no board meetings posted)", url: "https://www.youtube.com/" },
      { title: "Other meetings: board minutes on the ETBs' websites (Dublin and Dún Laoghaire, Kerry, Limerick and Clare, Waterford and Wexford, Kilkenny and Carlow), listed November 2026", url: "https://www.ddletb.ie/minutes/" },
      { title: "Enrollment: Department of Education, Data on Individual Schools, primary and special schools 2024/25 (census date 30 September 2024)", url: "https://www.gov.ie/en/department-of-education/collections/primary-schools-enrolment-figures/" },
      { title: "Enrollment: Department of Education, Data on Individual Schools, post-primary schools 2024/25", url: "https://www.gov.ie/en/department-of-education/collections/post-primary-schools-enrolment-figures/" },
      { title: "Public-school share, from the same school lists: pupils at schools run by a public body, counting a school as public when its patron is an ETB or the Minister for Education (Community National Schools and ETB special schools) or the Health Service Executive, or, after primary, when it is a vocational (ETB), community or comprehensive school. Church and other patrons\u2019 national schools and voluntary secondary schools are state-funded but privately run, so they count as private, the same rule as Belgium, the Netherlands and Spain", url: "https://www.gov.ie/en/department-of-education/collections/primary-schools-enrolment-figures/" },
      { title: "ETB sector overview (Education and Training Boards Ireland)", url: "https://www.etbi.ie/" }
    ],
    note: "Locales are estimates: population (children 5–17 divided by 0.178, their share of Ireland's population in Census 2022) over each ETB's land area; urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100. The Department of Education's school list couldn't be downloaded (gov.ie refused automated access), so there's no enrollment by ETB. Each board gets its region's overall poverty rate, so boards in the same region share a figure. The unemployment rate counts people who say their main status is unemployed or looking for a first job."
  },
  {
    only: "United Kingdom",
    group: "United Kingdom: councils, child low income and pupils",
    items: [
      { title: "Public-school share (England): independent schools' pupils in each local authority, Get Information about Schools full establishment extract, November 2026; against the state-funded pupils already used for enrollment", url: "https://get-information-schools.service.gov.uk/Downloads" },
      { title: "Child low income: DWP, Children in Low Income Families: local area statistics, financial year ending 2025 (Table 7, relative low income before housing costs, children under 16)", url: "https://www.gov.uk/government/statistics/children-in-low-income-families-local-area-statistics-2022-to-2025" },
      { title: "England's two-tier counties: ONS Local Authority District to County and Unitary Authority (December 2024) lookup (districts added up)", url: "https://geoportal.statistics.gov.uk/" },
      { title: "England pupils: Get Information about Schools, all establishments (open state-funded schools: council-maintained, academies, free schools and special schools), November 2026", url: "https://get-information-schools.service.gov.uk/Downloads" },
      { title: "Scotland pupils: Pupil census supplementary statistics 2025, Table 5.2", url: "https://www.gov.scot/publications/pupil-census-supplementary-statistics/" },
      { title: "Wales pupils: Schools' census results, January 2025, Table 5", url: "https://www.gov.wales/schools-census-results-january-2025" },
      { title: "Northern Ireland pupils: Annual enrolments at schools and in funded pre-school education, 2025/26 (primary 164,713, post-primary 156,766, special 7,729)", url: "https://datavis.nisra.gov.uk/DEstatistics/annual-enrolments-schools-and-funded-pre-school-education-northern-ireland-202526.html" },
      { title: "Borders: ONS Counties and Unitary Authorities (December 2024) Boundaries UK BUC", url: "https://geoportal.statistics.gov.uk/" },
      { title: "Meetings: each council's own YouTube channel (listed in the “Meetings source” column); videos whose titles name an education, schools, children's or young people's committee, panel or forum", url: "https://www.youtube.com/" },
      { title: "Other meetings: each council's ModernGov committee system (public web service: GetCommittees, GetMeetings), education and children's committees, 2010 to November 2026 (the site is in the “Other meetings source” column)", url: "https://www.moderngov.co.uk/" }
    ],
    note: "Locales are estimates: population (children under 16 divided by 0.185, their share of the UK population) over each council's land area from the ONS borders; urban 2,000+ people per km², suburban 500–2,000, mixed 100–500, rural under 100. England's pupil counts come from the register of schools (each school's latest census figure), so they can differ a little from the published census totals. Northern Ireland's Education Authority covers all 11 of its council areas. Channels the search wrongly matched (for example Bradford on Avon Town Council for Bradford) were checked by hand and left out (data-prep/inputs/uk/uk_channels.csv)."
  },
  {
    only: "Saint-Pierre-et-Miquelon (France)",
    group: "Saint-Pierre-et-Miquelon: schools, meetings and map",
    items: [
      { title: "Population and land area (for density): INSEE legal populations (Saint-Pierre 5,194, Miquelon-Langlade 596) and the communes' areas, via the government's geo API", url: "https://geo.api.gouv.fr/communes?codeDepartement=975&fields=nom,code,population,surface" },
      { title: "Service de l'Éducation nationale de Saint-Pierre-et-Miquelon (the French state's education office)", url: "https://www.education.gouv.fr/service-de-l-education-nationale-de-saint-pierre-et-miquelon-100136" },
      { title: "Enrollment: Repères et références statistiques 2025, chapter 11, La France d'outre-mer (tables 11.01: 358 primary and 484 secondary students, start of the 2024 school year)", url: "https://www.education.gouv.fr/sites/default/files/2025-07/rers2025-chapitre-11-441744.pdf" },
      { title: "Meetings: Territorial Council deliberations in the official gazette of Saint-Pierre-et-Miquelon (session dates)", url: "https://www.jo-spm.fr/" },
      { title: "Territorial Council rules: Code général des collectivités territoriales, book IV (Saint-Pierre-et-Miquelon)", url: "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006135519/" },
      { title: "Unemployment (stand-in for poverty): CIA World Factbook, Saint Pierre and Miquelon (8.7%, 2015 est.; population below poverty line: NA)", url: "https://relief.unboundmedicine.com/relief/view/The-World-Factbook/563198/all/Saint_Pierre_and_Miquelon" },
      { title: "Poverty: IEDOM, Saint-Pierre-et-Miquelon key figures 2023 (poverty rate listed as not available)", url: "https://www.iedom.fr/IMG/pdf/st_pierre_et_miquelon_2023_chiffres_cles.pdf" },
      { title: "Map outline: Natural Earth 1:10m admin-0 map units", url: "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/" }
    ],
    note: "The Territorial Council's website (spm-ct975.fr) refused automated access, so session dates come from the deliberations in the official gazette; no recordings of its sessions were found. The council handles the archipelago's own affairs; schools are run by the French state."
  },
  {
    only: "Canada",
    group: "Canada: children and low income",
    items: [
      { title: "Statistics Canada table 98-10-0103-01: low-income status by age, 2021 Census (census subdivisions; children 0–17, LIM-AT, 2020 incomes)", url: "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810010301" },
      { title: "Statistics Canada 2021 census subdivision boundary file (lcsd000b21a_e), copied to this project's GitHub release because Statistics Canada's site blocks automated downloads", url: "https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/tag/statcan-csd-2021" },
      { title: "Statistics Canada: low-income measure, after tax (LIM-AT) definition", url: "https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/Definition-eng.cfm?ID=fam021" },
      { title: "Wood Buffalo population and the Fort McMurray population centre (2021 Census), used to share Wood Buffalo's children between its boards", url: "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&DGUIDlist=2021A00054816037&GENDERlist=1&STATISTIClist=1&HEADERlist=0" }
    ],
    note: "Locale (estimated): each census subdivision with 100,000+ people (Statistics Canada's “large urban” size, in that table's total population) is large urban; one with at least 150 people per km² is medium urban (30,000–99,999) or small urban (1,000–29,999); the rest are rural. A board takes the locale where most of its children live. Each board's figures add up the census subdivisions (municipalities, reserves and unorganized areas) inside its border; a subdivision split between boards is shared by land area, which can be off where most people live in one part of it. Boards in the same place (public and Catholic, English and French) share the same children, so their figures can't be added together. Statistics Canada doesn't work out low-income status on First Nations reserves, so children living on reserves aren't counted (their schools are mostly run by First Nations, not these boards)."
  },
  {
    only: "Canada",
    group: "Canada: school board borders",
    items: [
      { title: "First Nations reserves and settlements outside every school board (Ontario and Alberta): Statistics Canada, 2021 census subdivision boundaries (lcsd000b21a_e), types IRI and S-É", url: "https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/tag/statcan-csd-2021" },
      { title: "British Columbia: school district boundaries (DataBC)", url: "https://catalogue.data.gov.bc.ca/dataset/school-districts-of-bc" },
      { title: "Alberta: public and separate school authority boundaries, 2025 (Alberta geospatial services)", url: "https://geospatial.alberta.ca/titan/rest/services" },
      { title: "Saskatchewan: schools and school divisions (Government of Saskatchewan map service)", url: "https://gis.saskatchewan.ca/arcgis/rest/services/Education/SchoolsAndDivisions/MapServer" },
      { title: "Manitoba: school divisions (Manitoba geoportal)", url: "https://geoportal.gov.mb.ca/" },
      { title: "Ontario: school board boundaries (Land Information Ontario)", url: "https://geohub.lio.gov.on.ca/" },
      { title: "Quebec: centres de services scolaires and English school boards (Données Québec)", url: "https://www.donneesquebec.ca/recherche/dataset/territoires-des-commissions-scolaires-du-quebec" }
    ],
    note: "Nova Scotia, New Brunswick and the Northwest Territories publish no border files, so their boards are built from the counties or regions they serve. Boards that serve a whole province or territory use its total."
  },
  {
    only: "Canada",
    group: "Canada: enrollment",
    items: [
      { title: "Population, land area and children aged 5–17 by census subdivision, 2021 Census: Statistics Canada tables 98-10-0002-01 (population and dwelling counts) and 98-10-0022-01 (age in single years). Used for each board's people per km² (census subdivisions inside its border, split ones shared by land area) and the estimated enrollment of First Nations reserves outside every board (data-prep/add_canada_population.py)", url: "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002201" },
      { title: "Ontario: School Information and Student Demographics, 2024–25 (school enrolment summed by board; Ontario Data Catalogue)", url: "https://data.ontario.ca/dataset/school-information-and-student-demographics" },
      { title: "Quebec: Évolution de l'effectif des centres de services scolaires et des commissions scolaires, September 2022 (Ministry of Education)", url: "https://cdn-contenu.quebec.ca/cdn-contenu/education/indicateurs-statistiques/Previsions_effectif_scolaire/Faits_saillants/evolution-effectif-scolaire.pdf" },
      { title: "British Columbia: BC Schools – Student Headcount by Grade, 2025/26 public schools (DataBC)", url: "https://catalogue.data.gov.bc.ca/dataset/7114187e-305c-4a79-acbb-3294ba0f53c8" },
      { title: "British Columbia public-school share: the same file’s independent (private) schools, 2025/26, placed in the school district their school number starts with (independent online schools, which teach province-wide, left out). Public = the board’s own pupils; francophone-board (CSF) pupils aren’t counted on either side. Other provinces have overlapping public, Catholic and francophone boards, so they get no figure", url: "https://catalogue.data.gov.bc.ca/dataset/7114187e-305c-4a79-acbb-3294ba0f53c8" },
      { title: "Alberta: student enrolment by school authority, 2024/25 (Alberta Open Data)", url: "https://open.alberta.ca/opendata/ccbcf0fb-615e-44a0-b7ec-681e2ea4e1e7" },
      { title: "Manitoba: Enrolment Report, October 1, 2025 (Manitoba Education)", url: "https://www.edu.gov.mb.ca/k12/finance/sch_enrol/enrolment_2025.pdf" },
      { title: "Nova Scotia: Public School Enrolment by RCE/CSAP and School, 2025–26 (Nova Scotia Open Data)", url: "https://data.novascotia.ca/Education/Nova-Scotia-Public-School-Enrolment-by-RCE-CSAP-and/cjnf-ywvt" },
      { title: "New Brunswick: student enrolment by school and grade, 2024–25 (GNB open data)", url: "https://open.canada.ca/data/en/dataset/712e7355-91d7-7b4f-9d46-1e7b5561cd95" },
      { title: "Saskatchewan: Active List of Saskatchewan Schools/Programs, K-12 headcount as of September 30, 2024 (Ministry of Education; school figures summed by division; schools listed as fewer than 10 count as 5)", url: "https://publications.saskatchewan.ca/#/products/83293" },
      { title: "Northwest Territories: JK-12 Education System Performance Measures Technical Report 2024-25, Table 6 (full-time-equivalent enrolment, grades 1–12, by education body)", url: "https://www.ece.gov.nt.ca/sites/ece/files/resources/jk-12_annual_pm_report_2024-25_final.pdf" },
      { title: "Newfoundland and Labrador: Community Accounts, Enrolment 1990-2026 (province-wide, used for NLSchools)", url: "https://nl.communityaccounts.ca/table.asp?_=vb7En4WVgbOxz7ZjS6rIxpuixqOVko7Lqomyv4yplszCmJ6-x84_" },
      { title: "Newfoundland and Labrador French board: Conseil scolaire francophone provincial (“more than 400 students”)", url: "https://csfp.nl.ca/a-propos/" },
      { title: "Prince Edward Island: official K-12 enrolment, September 2023 (Public Schools Branch total, as quoted in search results)", url: "https://www.princeedwardisland.ca/en/node/71985" },
      { title: "PEI French board (Commission scolaire de langue française): CBC News, October 2023 (1,259 students)", url: "https://www.cbc.ca/news/canada/prince-edward-island/french-schools-pei-expansion-population-growth-immigration-1.6985246" },
      { title: "Yukon First Nation School Board: territorial school counts for 7 of its 11 schools (about 705 students), as compiled by the site owner", url: "https://yukon.ca/en/first-nation-school-board" },
      { title: "Yukon French board: People for Education, Canadian Education Blueprint (413 students, 2025–26)", url: "https://peopleforeducation.ca/blueprints/" },
      { title: "Nunavut French board: Radio Canada International, September 3, 2025 (116 students at École des Trois-Soleils)", url: "https://www.rcinet.ca/regard-sur-arctique/2025/09/03/plus-deleves-plus-de-depenses-dans-les-ecoles-francophones-des-territoires/" }
    ],
    note: "The provincial files are official. The last seven sources fill in boards with no provincial file and are noted in the “Enrollment note” column; NLSchools uses the province-wide total, which also includes the French board's roughly 400 students. Lloydminster's two divisions report to both Alberta and Saskatchewan, so each side shows that province's count, which may overlap. The Yukon First Nation School Board's figure covers 7 of its 11 schools, so it undercounts. The years differ by province (see the Enrollment year column)."
  },
  {
    only: "Canada",
    group: "Canada: board meetings",
    items: [
      { title: "Each board's own YouTube channel (listed in the “Meetings source” column)", url: "https://www.youtube.com/" },
      { title: "Civic Searchlight (checked; covers city councils and police boards, not school boards)", url: "https://nmc-mic.ca/2025/10/09/civic-searchlight-accountability-tool-launches/" }
    ],
    note: "Each board's channel was found by searching YouTube for the board's name (and its acronym or French name); channels that turned out to belong to someone else, such as a US district with the same name, were checked by hand and left out. Videos whose titles show a meeting of the board or one of its committees (“meeting”, or the French “séance” or “réunion”) were counted, leaving out information sessions, trainings and similar events; a meeting split into parts counts once. Meetings streamed only on Zoom, Facebook or a board's own site aren't counted, so 0 doesn't mean a board holds no public meetings."
  },
  {
    only: "Canada",
    group: "Canada: provincial rules on recording or streaming board meetings (checked November 3, 2026)",
    items: [
      { title: "Ontario: O. Reg. 463/97, Electronic Meetings and Meeting Attendance (Education Act)", url: "https://www.ontario.ca/laws/regulation/970463" },
      { title: "Global News: Ontario school boards under supervision told to stop livestreaming meetings (October 2025)", url: "https://globalnews.ca/news/11472398/ontario-school-board-live-streaming-meeting-change" },
      { title: "CBC News: Ottawa parent fights back after school board stops livestreaming committee meetings", url: "https://www.cbc.ca/news/canada/ottawa/ottawa-parent-fights-back-after-school-board-stops-livestreaming-committee-meetings-9.6933871" },
      { title: "Quebec: Education Act (Loi sur l'instruction publique, I-13.3), sections 162 and 167", url: "https://www.legisquebec.gouv.qc.ca/fr/document/lc/i-13.3" },
      { title: "St. Albert Gazette: Alberta board debates posting meeting recordings (no provincial requirement)", url: "https://www.stalbertgazette.com/local-news/st-albert-public-schools-board-debates-public-access-to-meeting-recordings-11661194" }
    ],
    note: "No province or territory was found to require school boards to record or livestream meetings. Provincial school acts require open meetings and minutes; the statute details here are from summaries and should be checked against the current acts."
  },
  {
    only: "Texas",
    group: "Law",
    items: [
      { title: "FindLaw.com - Texas Government Code - GOV'T § 551.128. Internet Broadcast of Open Meeting - last updated January 01, 2026", url: "https://codes.findlaw.com/tx/government-code/gov-t-sect-551-128/" }
    ]
  },
  {
    only: "Texas",
    group: "County and ID checks (used for repeated district names)",
    items: [
      { title: "Highland Park ISD on Wikipedia", url: "https://en.wikipedia.org/wiki/Highland_Park_Independent_School_District" },
      { title: "Big Sandy ISD (Polk County) on Wikipedia", url: "https://en.wikipedia.org/wiki/Big_Sandy_Independent_School_District_(Polk_County,_Texas)" },
      { title: "Wylie ISD (Taylor County) on Wikipedia", url: "https://en.wikipedia.org/wiki/Wylie_Independent_School_District_(Taylor_County,_Texas)" },
      { title: "Dawson ISD (Navarro County) on Texas Tribune", url: "https://schools.texastribune.org/districts/dawson-isd-navarro/grade/" },
      { title: "Midway ISD (Clay County) on Wikipedia", url: "https://en.wikipedia.org/wiki/Midway_High_School_(Clay_County,_Texas)" },
      { title: "Rice Consolidated ISD on Wikipedia", url: "https://en.wikipedia.org/wiki/Rice_Consolidated_Independent_School_District" },
      { title: "Northside ISD on Wikipedia", url: "https://en.wikipedia.org/wiki/Northside_Independent_School_District" },
      { title: "Valley View ISD (Cooke County) on Wikipedia", url: "https://en.wikipedia.org/wiki/Valley_View_Independent_School_District_(Cooke_County,_Texas)" },
      { title: "Edgewood ISD (Van Zandt County) on Texas Tribune", url: "https://schools.texastribune.org/districts/edgewood-isd-van-zandt/grade/" },
      { title: "Hubbard ISD (Hill County) on Texas Tribune", url: "https://schools.texastribune.org/districts/hubbard-isd-hill/grade/" },
      { title: "Chapel Hill ISD (Titus County) on Wikipedia", url: "https://en.wikipedia.org/wiki/Chapel_Hill_Independent_School_District_(Titus_County,_Texas)" },
      { title: "Centerville ISD (Leon County) on Texas Tribune", url: "https://schools.texastribune.org/districts/centerville-isd-leon/graduation/" }
    ]
  },
  {
    only: "Texas",
    group: "Other",
    items: [
      { title: "Rockport-Fulton / Aransas County (from the CivicSearch list), for the Aransas County page’s 16 meetings", url: "https://schools.civicsearch.org/cities" }
    ],
    note: "Inferred counties (Big Sandy, Chapel Hill, Centerville, Hubbard, Midway McLennan, Valley View Hidalgo, Edgewood Bexar, and Wylie Collin) came from size and ID matches. They are not confirmed by a source."
  },
  {
    only: ["Texas", "United States"],
    group: "State rules: laws (checked October 29, 2026)",
    items: [
      { title: "Texas Government Code § 551.128 (Internet broadcast of open meeting; 10,000+ student districts)", url: "https://texas.public.law/statutes/tex._gov't_code_section_551.128" },
      { title: "Texas SB 413 (2025), amending Education Code § 11.0621 (every school board records each meeting)", url: "https://capitol.texas.gov/tlodocs/89R/billtext/html/SB00413F.htm" },
      { title: "Oregon ORS 192.655 (recording requirements for school district boards), in ORS chapter 192", url: "https://www.oregonlegislature.gov/bills_laws/ors/ors192.html" },
      { title: "Louisiana R.S. 42:23 (audio and video recordings; live broadcast)", url: "https://www.legis.la.gov/legis/Law.aspx?d=99525" },
      { title: "Montana Code 2-3-214 (recording of meetings for certain boards)", url: "https://mca.legmt.gov/bills/mca/title_0020/chapter_0030/part_0020/section_0140/0020-0030-0020-0140.html" },
      { title: "Montana Code 20-6-201 (school district classes by population)", url: "https://mca.legmt.gov/bills/mca/title_0200/chapter_0060/part_0020/section_0010/0200-0060-0020-0010.html" },
      { title: "Indiana Office of Technology guidance on IC 5-14-1.5-2.9 (video streaming of public meetings)", url: "https://www.in.gov/iot/files/20260818-Video-treaming-of-Public-Meetings-Guidance-REVISED.pdf" },
      { title: "South Carolina Act 28 of 2025 (Bill 77), adding Code § 59-19-85 (school board livestreaming)", url: "https://www.scstatehouse.gov/sess126_2025-2026/bills/77.htm" },
      { title: "New Mexico SB 137 (2024), adding NMSA 22-5-4.16 (school board webcasting and archiving)", url: "https://www.nmlegis.gov/Sessions/24%20Regular/final/SB0137.pdf" },
      { title: "West Virginia Board of Education rule, W. Va. Code R. § 126-12-6 (board meetings live-streamed and posted)", url: "https://www.law.cornell.edu/regulations/west-virginia/W-Va-C-S-R-SS-126-12-6" },
      { title: "Delaware Code Title 14 § 208 (digital recording of board meetings)", url: "https://delcode.delaware.gov/title14/c002/sc01/index.html" },
      { title: "Vermont 1 V.S.A. § 312 (meeting recordings for local public bodies, Act 133 of 2024)", url: "https://legislature.vermont.gov/statutes/section/01/005/00312" },
      { title: "Vermont Agency of Education guidance on the Open Meeting Law and Act 133", url: "https://education.vermont.gov/sites/aoe/files/edu-the-open-meeting-law-and-public-records-act.pdf" },
      { title: "Utah Code § 52-4-203 (written minutes and recording of open meetings)", url: "https://le.utah.gov/xcode/Title52/Chapter4/52-4-S203.html" },
      { title: "Washington RCW 42.30.035 (audio recording of school board meetings)", url: "https://app.leg.wa.gov/RCW/default.aspx?cite=42.30.035" },
      { title: "New York Public Officers Law § 103-a (videoconferencing by public bodies)", url: "https://newyork.public.law/laws/n.y._public_officers_law_section_103-a" }
    ]
  },
  {
    only: ["Texas", "United States"],
    group: "State rules: bills that are not law, and summaries used to find the laws",
    items: [
      { title: "Maryland SB 99 (2026), Local Boards of Education Transparency Act", url: "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0099?ys=2026RS" },
      { title: "Rhode Island H 7676 (2026)", url: "https://www.billtrack50.com/billdetail/1969833" },
      { title: "Colorado HB24-1168, Equal Access to Public Meetings", url: "https://leg.colorado.gov/bills/hb24-1168" },
      { title: "Mississippi SB 2571 (2025)", url: "https://www.billtrack50.com/billdetail/1799961" },
      { title: "Wyoming HB 191 (2026), school board meeting requirements", url: "https://wyoleg.gov/Legislation/2026/HB0191" },
      { title: "Arizona governor vetoes school board livestream requirement (HB 2380)", url: "https://thebeam.org/arizona-school-board-recording-veto-hb2380/" },
      { title: "Arkansas HB 1836 (2025)", url: "https://arkleg.state.ar.us/Bills/Detail?id=HB1836&ddBienniumSession=2025%2F2025R" },
      { title: "Georgia HB 989 (2025–2026)", url: "https://www.legis.ga.gov/api/legislation/document/20252026/239936" },
      { title: "Teleport: open meeting law recording requirements by state (used to find laws)", url: "https://www.teleport-app.com/open-meeting-law-recording-requirements-by-state" },
      { title: "Diligent: livestreaming regulations for public boards (used to find laws)", url: "https://www.diligent.com/resources/blog/regulations-livestreaming" },
      { title: "TASB: three things to know about new school board meeting requirements (Texas SB 413)", url: "https://www.tasb.org/news-insights/three-things-to-know-about-new-school-board-meeting-requirements" }
    ]
    },
  {
    only: ["United States", "Japan", "Iceland", "Germany", "Belgium", "Islands and microstates", "Croatia", "Italy", "France", "Philippines", "Spain"],
    group: "Enrollment estimates (places with no published pupil count)",
    items: [
      { only: "United States", title: "Districts with no NCES enrollment: children aged 5–17 from the Census SAIPE 2024 school district file (above)", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/ussd24.csv" },
      { only: ["Japan", "Iceland", "Germany", "Belgium", "Islands and microstates"], title: "School-age share of each place's own children figure (the children column already in the data, from the sources above): Japan 6–14 of under 15, Iceland 6–15 of under 18, Germany 6–17 of under 18, Belgium 6–14 of under 18, islands 6–14 of 0–14" },
      { only: ["Croatia", "Italy", "France"], title: "Eurostat, population on 1 January by age group, sex and NUTS 3 region (demo_r_pjangrp3), 2024: each region's share of school ages (Croatia 7–14, Italy 6–13, France 3–10), times the place's population", url: "https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjangrp3/default/table" },
      { only: ["Croatia", "Italy", "France"], title: "Eurostat / GISCO, correspondence of local administrative units (LAU) to NUTS 2024 regions", url: "https://ec.europa.eu/eurostat/web/nuts/local-administrative-units" },
      { only: "Philippines", title: "Philippines subnational population statistics by age (PSA projections, 2025), via the Humanitarian Data Exchange (HDX, phl_admpop): each province's share of children aged 5–17", url: "https://data.humdata.org/dataset/cod-ps-phl" },
      { only: "Spain", title: "Pupils by municipality, Catalonia: Departament d'Educació, “Alumnes matriculats per ensenyament i unitats dels centres docents”, 2025-26 (Transparència Catalunya open data); public-school share from the same dataset by the school's nature (public, or private, which includes state-funded concertada schools)", url: "https://analisi.transparenciacatalunya.cat/d/xvme-26kg" },
      { only: "Spain", title: "Pupils by municipality, Valencian Community: Conselleria d'Educació, “Resumen de escolarización 2025” (pupils by school, summed by its municipality; infantil to bachillerato, public and private)", url: "https://dadesobertes.gva.es/dataset/edu-alu-gen-2025" },
      { only: "Spain", title: "Pupils by municipality, Community of Madrid: “Alumnos no universitarios matriculados en centros escolares por tipo de centro y régimen. Municipios”, 2024-25 (régimen general)", url: "https://datos.comunidad.madrid/dataset/alumnos_no_universitarios_por_tipo_y_regimen" },
      { only: "Spain", title: "Estimates elsewhere: INE, annual population census 2024, population aged 15+ by level of studies in progress, municipalities of 500+ (table 66627), plus children aged 3–14 (twelve eighteenths of the estimated children under 18)", url: "https://www.ine.es/jaxiT3/Tabla.htm?t=66627" }
    ],
    note: "Estimates are marked on the map and in the Enrollment estimated column. Built by data-prep/estimate_enrollment.py, with prep_enrollment_shares.py, prep_spain_pupils.py and prep_spain_regional_pupils.py."
  }
];
