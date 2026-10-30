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
      { only: "United States", title: "Census SAIPE 2024 state and county estimates (all-ages poverty rate, used for the 5 districts with no children ages 5–17; see the Poverty note column)", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-state-and-county/est24all.txt" }
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
      { only: "United States", title: "NCES 2018–2022 directory data, used for the latest enrollment or locale of districts missing them in 2023 (e.g., New York City)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2022/" },
      { only: "U.S. territories", title: "NCES 2023 directory data (schools, enrollment and locale for the territories: Puerto Rico, Guam, Northern Mariana Islands, U.S. Virgin Islands, American Samoa)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/" },
      { only: "U.S. territories", title: "NCES 2021 directory data (Guam enrollment: 26,619; NCES has none for Guam after 2021)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2021/?fips=66" },
      { only: "U.S. territories", title: "NCES 2020 directory data (American Samoa enrollment: 10,246; NCES has none for American Samoa after 2020)", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2020/?fips=60" }
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
      { title: "Government Access Channel – Virgin Islands on YouTube (checked; no board meeting recordings)", url: "https://www.youtube.com/channel/UCUeosYkcAS4HVKSfbLNR0FA" },
      { title: "American Samoa Department of Education website (could not be reached October 30, 2026; YouTube searches found no board meeting recordings)", url: "https://www.doe.as/" },
      { title: "Puerto Rico Department of Education: run as a cabinet department, with no school board" },
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
    group: "Map (district borders)",
    items: [
      { title: "Census Bureau 2024 cartographic boundary files: unified school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_unsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: elementary school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_elsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: secondary school districts", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_scsd_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: states and territories (outlines for Guam, the Northern Mariana Islands and American Samoa)", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip" },
      { title: "Census Bureau 2024 cartographic boundary files: counties (the U.S. Virgin Islands' islands, for its two districts)", url: "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip" },
      { title: "Background map: © OpenStreetMap contributors, © CARTO", url: "https://carto.com/attributions" }
    ],
    note: "Borders were simplified with mapshaper so the map loads quickly; they are drawn with Leaflet."
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
  }
];
