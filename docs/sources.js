// Sources shown on the page, grouped. Add `url` to an item to make it a link.
// `only: "<data set name>"` on a group or item shows it just for that data set.
window.SOURCES = [
  {
    group: "Census data (children ages 5–17 and children in poverty)",
    items: [
      { only: "Texas", title: "Census SAIPE 2024 Texas school district file", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/sd24-tx.txt" },
      { title: "Census SAIPE 2024 school district estimates page, which describes the file layout", url: "https://www.census.gov/data/datasets/2024/demo/saipe/2024-school-districts.html" },
      { title: "SAIPE school district overview, which confirms the ages 5–17 measures", url: "https://census.gov/programs-surveys/saipe/technical-documentation/methodology/school-districts/overview-school-district.html" },
      { only: "United States", title: "Census SAIPE 2024 file for all US school districts", url: "https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/ussd24.csv" }
    ]
  },
  {
    group: "Meeting counts (available board meetings)",
    items: [
      { only: "Texas", title: "CivicSearch Texas district list", url: "https://schools.civicsearch.org/cities" },
      { only: "Texas", title: "Individual CivicSearch district pages, such as Alamo Heights ISD. All 74 Texas district pages were checked.", url: "https://schools.civicsearch.org/alamo-heights-isd-texas" },
      { only: "United States", title: "CivicSearch school district list", url: "https://schools.civicsearch.org/cities" },
      { only: "United States", title: "CivicSearch district list data (the meeting counts behind the district list, for every state; downloaded October 29, 2026)", url: "https://schools.civicsearch.org/api/get_place_list" },
      { only: "United States", title: "USLege school board coverage, such as Carrollton-Farmers Branch ISD (checked, not used for counts)", url: "https://www.uslege.ai/tracking/carrollton-farmers-branch-independent-school-district" }
    ],
    note: "USLege covers about 60 school districts nationwide and counts only the last six months of meetings, so its numbers aren't comparable with CivicSearch's and weren't used."
  },
  {
    group: "Enrollment and urban/suburban/rural type",
    items: [
      { title: "NCES Common Core of Data 2023 school district directory (enrollment and locale codes), via the Urban Institute Education Data API", url: "https://educationdata.urban.org/documentation/school-districts.html" },
      { only: "United States", title: "NCES 2023 directory data for all US school districts", url: "https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/" }
    ]
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
  }
];
