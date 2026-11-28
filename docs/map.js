// "Map" tab: school district borders (Census 2024 cartographic boundaries, in docs/data/map/)
// colored by the site's data. app.js calls SiteMap.show() when the tab or the data set changes.
(function () {
  const $ = (id) => document.getElementById(id);
  const LAYERS = ["world", "unsd", "elsd", "territories", "scsd", "canada", "spm", "uk", "ireland", "norway", "sweden", "finland", "denmark", "netherlands", "germany", "new-zealand", "islands", "iceland", "switzerland", "chile", "colombia", "brazil", "mexico", "peru", "spain", "france", "ecuador", "italy", "poland", "japan", "portugal", "belgium", "australia", "croatia", "latvia", "estonia", "argentina", "israel", "slovenia", "taiwan", "uruguay", "costa_rica", "lithuania", "south_africa", "kenya", "georgia", "south_korea", "india", "philippines", "malaysia", "indonesia", "paraguay", "czechia", "rwanda", "sri_lanka", "canada-fn"];   // files in data/map/; scsd only when ticked
  // Canadian boards overlap (public and Catholic, English and French). The main layer shows one
  // board per place; "canada2" holds the overlapping ones and shows when its box is ticked.
  // Quebec's French boards cover all of Quebec; elsewhere the public (or English) board does.
  // Quebec's Cree, Kativik and Littoral boards ("Special status") serve the north and east instead.
  const caMainRow = (r) => !!r && (r.pseudo || ["Public", "English public", "Special status"].includes(r["Board type"]) ||
    r["Board type"] === (r.Province === "Quebec" ? "French" : "English"));
  // The Nordic countries and the Netherlands: municipalities, IDs like "NO-0301" (map file per country).
  // Also Germany, New Zealand and the island countries ("ISLE-JAM"), which share the same handling.
  const EU = { NO: "norway", SE: "sweden", FI: "finland", DK: "denmark", NL: "netherlands", DE: "germany", NZ: "new-zealand", ISLE: "islands", IS: "iceland", CH: "switzerland", CL: "chile", CO: "colombia", MX: "mexico", BR: "brazil", PE: "peru", ES: "spain", FRA: "france", EC: "ecuador", IT: "italy", PL: "poland", JP: "japan", PT: "portugal", BE: "belgium", AU: "australia", HR: "croatia", LV: "latvia", EE: "estonia", ARG: "argentina", ISR: "israel", SVN: "slovenia", TWN: "taiwan", URY: "uruguay", CRI: "costa_rica", LTU: "lithuania", ZAF: "south_africa", KEN: "kenya", GEO: "georgia", KOR: "south_korea", IND: "india", PH: "philippines", MYS: "malaysia", IDN: "indonesia", PRY: "paraguay", CZE: "czechia", RWA: "rwanda", LKA: "sri_lanka" };
  const EU_NAMES = { NO: "Norway", SE: "Sweden", FI: "Finland", DK: "Denmark", NL: "Netherlands", DE: "Germany", NZ: "New Zealand", ISLE: "the islands and microstates", IS: "Iceland", CH: "Switzerland", CL: "Chile", CO: "Colombia", MX: "Mexico", BR: "Brazil", PE: "Peru", ES: "Spain", FRA: "France", EC: "Ecuador", IT: "Italy", PL: "Poland", JP: "Japan", PT: "Portugal", BE: "Belgium", AU: "Australia", HR: "Croatia", LV: "Latvia", EE: "Estonia", ARG: "Argentina", ISR: "Israel", SVN: "Slovenia", TWN: "Taiwan", URY: "Uruguay", CRI: "Costa Rica", LTU: "Lithuania", ZAF: "South Africa", KEN: "Kenya", GEO: "Georgia", KOR: "South Korea", IND: "India", PH: "Philippines", MYS: "Malaysia", IDN: "Indonesia", PRY: "Paraguay", CZE: "Czechia", RWA: "Rwanda", LKA: "Sri Lanka" };
  const EU_POV = "Percentage of Children in Low Income";
  // Countries whose map figure is an all-ages poverty rate (no child rate by place).
  const ALL_AGES = new Set(["CL", "CO", "MX", "BR", "PE", "FRA", "EC", "IT", "JP", "PT", "BE", "AU", "HR", "EE", "ARG", "ISR", "SVN", "TWN", "URY", "CRI", "LTU", "ZAF", "GEO", "KOR", "IND", "PH", "MYS", "IDN", "PRY", "CZE", "RWA", "LKA"]);
  const povCol = (eu) => (eu === "ISLE" ? "Poverty rate or stand-in" : ALL_AGES.has(eu) ? "Poverty rate (all ages)" : EU_POV);
  const euOf = (id) => { const c = String(id).split("-")[0]; return String(id).includes("-") && EU[c] ? c : null; };
  const DRAW = ["world", "unsd", "elsd", "territories", "scsd", "canada", "canada2", "canada-fn", "spm", "uk", "ireland", ...Object.values(EU)];
  const gid = (f) => f.properties.GEOID || f.properties.id;
  const isCA = (id) => String(id).startsWith("CA-");
  const isFR = (id) => String(id).startsWith("FR-");   // Saint-Pierre-et-Miquelon (France)
  const isUK = (id) => String(id).startsWith("UK-");   // United Kingdom education authorities
  const isIE = (id) => String(id).startsWith("IE-");   // Ireland's Education and Training Boards
  const UK_POV = "Percentage of Children Under 16 in Low Income";
  const JUMPS = {
    "Contiguous US": [[24.4, -125], [49.5, -66.9]],
    Alaska: [[51.2, -179.5], [71.5, -129.9]],
    Hawaii: [[18.8, -160.4], [22.3, -154.7]],
    "Puerto Rico": [[17.85, -67.3], [18.55, -65.2]],
    "U.S. Virgin Islands": [[17.65, -65.1], [18.45, -64.55]],
    Guam: [[13.2, 144.6], [13.7, 145.0]],
    "Northern Mariana Islands": [[14.0, 144.8], [15.4, 146.0]],
    "American Samoa": [[-14.6, -171.1], [-14.1, -168.1]],
    Canada: [[42, -142], [66, -53]],
    "United States and Canada": [[18, -165], [68, -52]],
    "Saint-Pierre-et-Miquelon": [[46.72, -56.45], [47.17, -56.07]],
    "United Kingdom": [[49.9, -8.2], [58.7, 1.8]],
    Ireland: [[51.4, -10.6], [55.4, -5.9]],
    Norway: [[57.9, 4.5], [71.2, 31.1]],
    Sweden: [[55.3, 11.0], [69.1, 24.2]],
    Finland: [[59.7, 19.4], [70.1, 31.6]],
    Denmark: [[54.5, 8.0], [57.8, 15.2]],
    Netherlands: [[50.7, 3.3], [53.6, 7.3]],
    Germany: [[47.2, 5.8], [55.1, 15.1]],
    Iceland: [[63.2, -24.6], [66.6, -13.4]],
    Switzerland: [[45.8, 5.9], [47.9, 10.6]],
    Chile: [[-56.0, -76.0], [-17.4, -66.4]],
    Mexico: [[14.4, -118.5], [32.8, -86.6]],
    Brazil: [[-33.8, -74.0], [5.3, -34.8]],
    Peru: [[-18.4, -81.4], [0.0, -68.6]],
    Spain: [[35.9, -9.4], [43.8, 4.4]],
    France: [[41.3, -5.2], [51.1, 9.6]],
    "La Réunion": [[-21.4, 55.2], [-20.85, 55.85]],
    Guadeloupe: [[15.8, -61.85], [16.55, -61.0]],
    Martinique: [[14.38, -61.25], [14.9, -60.8]],
    "French Guiana": [[2.1, -54.6], [5.8, -51.6]],
    Mayotte: [[-13.05, 45.0], [-12.6, 45.3]],
    Ecuador: [[-5.1, -81.1], [1.5, -75.2]],
    Colombia: [[-4.3, -79.1], [12.6, -66.8]],
    "New Zealand": [[-47.4, 166.3], [-34.3, 178.7]],
    "Italy": [[35.4, 6.6], [47.1, 18.6]],
    "Poland": [[49.0, 14.1], [54.9, 24.2]],
    "Japan": [[24.0, 122.9], [45.6, 146.0]],
    "Portugal": [[32.6, -31.3], [42.2, -6.2]],
    "Belgium": [[49.45, 2.5], [51.55, 6.45]],
    "Australia": [[-44.0, 112.5], [-9.9, 154.0]],
    "Croatia": [[42.3, 13.4], [46.6, 19.5]],
    "Latvia": [[55.6, 20.9], [58.1, 28.3]],
    "Estonia": [[57.5, 21.7], [59.8, 28.3]],
    "Argentina": [[-55.2, -73.6], [-21.7, -53.6]],
    "Israel": [[29.4, 34.2], [33.4, 35.9]],
    "Slovenia": [[45.4, 13.3], [46.9, 16.6]],
    "Taiwan": [[21.8, 118.1], [26.4, 122.1]],
    "Uruguay": [[-35.1, -58.5], [-30.0, -53.0]],
    "Costa Rica": [[8.0, -86.0], [11.3, -82.5]],
    "Lithuania": [[53.8, 20.9], [56.5, 26.9]],
    "South Africa": [[-35.0, 16.4], [-22.1, 33.0]],
    "Kenya": [[-4.8, 33.9], [5.1, 42.0]],
    "Georgia": [[41.0, 40.0], [43.6, 46.8]],   // the country (EU_NAMES), not the US state
    "South Korea": [[33.1, 124.6], [38.7, 131.0]],
    "India": [[6.5, 68.0], [35.7, 97.5]],
    "Philippines": [[4.4, 116.8], [21.2, 127.0]],
    "Malaysia": [[0.8, 99.6], [7.5, 119.3]],
    "Indonesia": [[-11.2, 94.8], [6.3, 141.2]],
    "Paraguay": [[-27.7, -62.7], [-19.2, -54.2]],
    "Czechia": [[48.5, 12.0], [51.1, 18.9]],
    "Rwanda": [[-2.9, 28.8], [-1.0, 30.95]],
    "Sri Lanka": [[5.8, 79.5], [9.9, 82.0]],
    World: [[-58, -170], [75, 180]]
  };
  // Countries whose poverty figure is a welfare rate, far lower than a poverty rate: a map scale of their own.
  const OWN_SCALE = { JP: "welfare", PT: "welfarePT", BE: "welfareBE", LV: "welfarePT", EE: "welfare", SVN: "benefitSI", TWN: "welfarePT", URY: "welfarePT", CRI: "ipmCR", ZAF: "quintileZA", GEO: "tsaGE", KOR: "nblsKR" };
  const SCALES = {
    poverty: {
      column: "Percentage of Children Ages 5-17 in Poverty",
      caColumn: "Percentage of Children Ages 0-17 in Low Income",   // Canada's measure (not the same as the US one)
      // Darker reds above 30%, up to 80%: Mexico, Brazil, Colombia, Peru and Kenya have many places above 50%.
      breaks: [10, 15, 20, 25, 30, 40, 50, 60, 70, 80],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#cb2027", "#ad131a", "#8e0c13", "#6f080e", "#52050a", "#360306"],
      labels: ["Under 10%", "10–15%", "15–20%", "20–25%", "25–30%", "30–40%", "40–50%", "50–60%", "60–70%", "70–80%", "80% or more"]
    },
    // Japan's welfare rate is far lower than any poverty rate (few people claim welfare), so it has a scale of its own.
    welfare: {
      breaks: [0.5, 1, 1.5, 2, 3],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 0.5%", "0.5–1%", "1–1.5%", "1.5–2%", "2–3%", "3% or more"]
    },
    welfarePT: {
      breaks: [1, 2, 3, 5, 8],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 1%", "1–2%", "2–3%", "3–5%", "5–8%", "8% or more"]
    },
    welfareBE: {
      breaks: [0.5, 1, 2, 4, 6],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 0.5%", "0.5–1%", "1–2%", "2–4%", "4–6%", "6% or more"]
    },
    // Slovenia: benefits as a share of residents' net income.
    benefitSI: {
      breaks: [3, 4, 5, 6, 8],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 3%", "3–4%", "4–5%", "5–6%", "6–8%", "8% or more"]
    },
    // Costa Rica: UNDP's Multidimensional Poverty Index × 100, which runs below a poverty rate.
    ipmCR: {
      breaks: [3, 5, 7, 10, 15],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 3", "3–5", "5–7", "7–10", "10–15", "15 or more"]
    },
    // South Africa: public-school learners in quintile 1-3 (no-fee) schools.
    quintileZA: {
      breaks: [25, 50, 75, 90, 97],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 25%", "25–50%", "50–75%", "75–90%", "90–97%", "97% or more"]
    },
    // Georgia: families receiving the subsistence allowance per 100 residents.
    tsaGE: {
      breaks: [8, 11, 14, 18, 24],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 8", "8–11", "11–14", "14–18", "18–24", "24 or more"]
    },
    // South Korea: Basic Livelihood Security recipients per 100 residents.
    nblsKR: {
      breaks: [4, 5, 6, 7, 8],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 4%", "4–5%", "5–6%", "6–7%", "7–8%", "8% or more"]
    },
    // Comparable across countries: where a place falls among its own country's places (app.js adds it).
    rank: {
      column: "Poverty rank in country",
      breaks: [20, 40, 60, 80],
      colors: ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],
      labels: ["Lowest fifth (0–19)", "20–39", "40–59", "60–79", "Highest fifth (80–100)"]
    },
    meetings: {
      column: "Available Board Meetings",
      breaks: [1, 5, 15, 30],
      colors: ["#deebf7", "#9ecae1", "#4292c6", "#2171b5", "#08306b"],
      labels: ["0", "1–4", "5–14", "15–29", "30 or more"]
    },
    // Pupils, as each country counts them (see each view's note): at the place's schools, or living there.
    enrollment: {
      column: "Enrollment",
      breaks: [100, 500, 2000, 10000, 50000],
      colors: ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"],
      labels: ["Under 100", "100–499", "500–1,999", "2,000–9,999", "10,000–49,999", "50,000 or more"]
    },
    // People per km²; the 100, 500 and 2,000 breaks are the estimated locales' (rural, mixed, suburban, urban).
    density: {
      column: "People per km² (estimated)",
      breaks: [10, 50, 100, 500, 2000, 5000],
      colors: ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
      labels: ["Under 10 people per km²", "10–49", "50–99", "100–499", "500–1,999", "2,000–4,999", "5,000 or more"]
    },
    // Meetings found, against places of the same size: the share of its country's places in the same enrollment
    // tier (the By district size tab's tiers) that have fewer meetings found.
    peers: {
      breaks: [1, 25, 50, 75, 90],
      colors: ["#f7fcfd", "#bfd3e6", "#9ebcda", "#8c96c6", "#8856a7", "#810f7c"],
      labels: ["0% (more than none of them)", "1–24%", "25–49%", "50–74%", "75–89%", "90–100%"]
    },
    // How long ago the latest meeting found was held.
    recency: {
      breaks: [3, 12, 24, 60],
      colors: ["#006837", "#31a354", "#78c679", "#c2e699", "#ffffcc"],
      labels: ["Under 3 months ago", "3–11 months", "1–2 years", "2–5 years", "5 years or more"]
    },
    // Change in the poverty figure between the place's earliest and latest years ("Poverty by year"), in percentage
    // points: blue fell, red rose.
    change: {
      breaks: [-5, -2, -0.5, 0.5, 2, 5],
      colors: ["#2166ac", "#67a9cf", "#d1e5f0", "#f7f7f7", "#fddbc7", "#ef8a62", "#b2182b"],
      labels: ["Fell 5 points or more", "Fell 2–5 points", "Fell 0.5–2 points", "About the same (within 0.5)", "Rose 0.5–2 points", "Rose 2–5 points", "Rose 5 points or more"]
    },
    // Change in enrollment or population between the earliest and latest years given, in percent.
    changeEnr: {
      breaks: [-20, -5, -1, 1, 5, 20],
      colors: ["#8c510a", "#d8b365", "#f6e8c3", "#f5f5f5", "#c7eae5", "#5ab4ac", "#01665e"],
      labels: ["Fell 20% or more", "Fell 5–20%", "Fell 1–5%", "About the same (within 1%)", "Rose 1–5%", "Rose 5–20%", "Rose 20% or more"]
    },
    // Meetings found per year, counted from the first year with a meeting found, so a council that began posting
    // recently isn't ranked below one with a long archive.
    changePop: null,
    perYear: {
      breaks: [0.5, 2, 6, 12, 24],
      colors: ["#f7fbff", "#c6dbef", "#6baed6", "#3182bd", "#08519c", "#08306b"],
      labels: ["Under 0.5 a year (or none)", "0.5–1.9", "2–5.9", "6–11.9", "12–23.9", "24 or more a year"]
    },
    // Public schools' share of the pupils counted (for US districts: of public pupils plus private-school pupils
    // inside the district's border).
    public: {
      breaks: [50, 70, 80, 90, 95],
      colors: ["#feebe2", "#fcc5c0", "#fa9fb5", "#f768a1", "#c51b8a", "#7a0177"],
      labels: ["Under 50% in public schools", "50–69%", "70–79%", "80–89%", "90–94%", "95% or more"]
    }
  };
  SCALES.changePop = SCALES.changeEnr;
  // "In a chosen year": the usual scales, the value taken from the place's "... by year" column (the year menu picks it).
  SCALES.povYear = SCALES.poverty; SCALES.enrYear = SCALES.enrollment; SCALES.pubYear = SCALES.public;
  SCALES.changePub = SCALES.change;
  // Meetings recorded in a chosen year (from the dates in the recordings' titles, or CivicSearch's months).
  SCALES.meetYear = {
    breaks: [1, 3, 6, 12, 24],
    colors: ["#f7fbff", "#c6dbef", "#6baed6", "#3182bd", "#08519c", "#08306b"],
    labels: ["None that year", "1–2", "3–5", "6–11", "12–23", "24 or more"]
  };
  const YEAR_COL = { povYear: "Poverty by year", enrYear: "Enrollment by year", pubYear: "Public share by year", meetYear: "Meetings by year" };
  // Area of a border in km² (spherical polygons), for places whose data has a population but no density (US districts).
  const R_KM = 6371.0088, rad = (d) => d * Math.PI / 180;
  function ringArea(ring) {
    let a = 0;
    for (let i = 0; i < ring.length; i++) {
      const [x1, y1] = ring[i], [x2, y2] = ring[(i + 1) % ring.length];
      a += rad(x2 - x1) * (2 + Math.sin(rad(y1)) + Math.sin(rad(y2)));
    }
    return Math.abs(a * R_KM * R_KM / 2);
  }
  function geomArea(g) {
    if (!g) return 0;
    const polys = g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
    return polys.reduce((s, p) => s + ringArea(p[0]) - p.slice(1).reduce((h, r) => h + ringArea(r), 0), 0);
  }
  let areaById = null;
  function densityFor(row, id) {
    if (!row) return NaN;
    const d = toNumber(row["People per km² (estimated)"]);
    if (!isNaN(d)) return d;
    const pop = toNumber(row.Population);
    if (pop === 0) return 0;   // nobody lives there (a census count of 0)
    if (!(pop > 0)) return NaN;
    const land = toNumber(row["Land area (km²)"]);
    if (land > 0) return pop / land;
    // Layers drawn with lighter borders when zoomed out: the area of the full-detail border (data-prep/map_index.py).
    const hiArea = index && index._area && index._area[id];
    if (hiArea > 0) return pop / hiArea;
    if (!areaById) {
      areaById = {};
      Object.values(layers).forEach((l) => l.eachLayer((f) => { if (f.feature) { const k = gid(f.feature); areaById[k] = (areaById[k] || 0) + geomArea(f.feature.geometry); } }));
    }
    const a = areaById[id];
    return a > 0 ? pop / a : NaN;
  }
  const NO_DATA = "#9e9e9e";
  // Color by locale: one color per kind of place, from city to countryside (the Okabe-Ito palette, distinguishable with
  // the common kinds of colour blindness). Canada's own groups (large, medium and
  // small urban centres) share the colors of the closest US kinds. In "All", Canadian and European locales carry a
  // "Canada: " or country prefix, which is dropped here.
  const LOCALES = [
    { keys: ["Urban", "Large urban"], color: "#0072b2", label: "Urban (Canada: large urban centre)" },
    { keys: ["Suburban", "Medium urban"], color: "#56b4e9", label: "Suburban (Canada: medium urban centre)" },
    { keys: ["Town", "Small urban"], color: "#e69f00", label: "Town (Canada: small urban centre)" },
    { keys: ["Mixed"], color: "#cc79a7", label: "Mixed (estimated; outside the US and Canada)" },
    { keys: ["Rural"], color: "#009e73", label: "Rural" },
    { keys: ["Province-wide"], color: "#bdbdbd", label: "Canada: province- or territory-wide board", hide: true }
  ];
  const localeColor = (row) => {
    const loc = String((row && row.Locale) || "").trim().replace(/^[^:]+:\s*/, "");
    const g = LOCALES.find((x) => x.keys.includes(loc));
    return g ? g.color : NO_DATA;
  };
  const NO_DISTRICT = "#e3eedd";   // areas outside any school district (national parks, federal land, water)

  let searchIndex = [], highlight = null, active = -1, byId = new Map();
  let map = null, loading = null, lookup = {}, layers = {}, current = null, fips = {}, aliases = {};

  // Borders with no row of their own (Vermont town districts, pieces of districts merged in 2024)
  // show the figures of the district(s) listed in data/map/aliases.json; several are combined.
  function rowFor(geoid) {
    if (lookup[geoid]) return lookup[geoid];
    const a = aliases[geoid];
    if (!a) return null;
    if (a.rate) {   // left out of the Census poverty file: county all-ages rate
      return { District: a.district, "Percentage of Children Ages 5-17 in Poverty": a.rate, _povEst: true,
        "Available Board Meetings": 0, Enrollment: a.enrollment ?? "", "Map note": a.note };
    }
    const rows = a.ids.map((id) => lookup[id]).filter(Boolean);
    if (!rows.length) return null;
    const row = rows.length === 1 ? { ...rows[0] } : combine(rows);
    row["Map note"] = a.note;
    return row;
  }

  function combine(rows) {
    const sum = (c) => rows.reduce((t, r) => t + (toNumber(r[c]) || 0), 0);
    const kids = sum("Children Ages 5-17"), poor = sum("Children Ages 5-17 in Poverty");
    return {
      District: rows.map((r) => r.District).join(" + "), State: rows[0].State,
      "Children Ages 5-17": kids, "Children Ages 5-17 in Poverty": poor,
      "Percentage of Children Ages 5-17 in Poverty": kids ? (100 * poor) / kids : "",
      "Available Board Meetings": sum("Available Board Meetings"),
      Enrollment: rows.every((r) => r.Enrollment) ? sum("Enrollment") : "",
      Population: rows.every((r) => r.Population !== undefined && r.Population !== "") ? sum("Population") : "",
      Locale: rows[0].Locale
    };
  }

  const toNumber = (v) => {
    const s = String(v ?? "").trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  };

  // The poverty figure a place is coloured by: its own measure, else the stand-ins in order. With `last`, also a
  // figure the map would otherwise lack: Ecuador's 2010 NBI rate (the Galápagos) or the place's latest earlier year.
  function povValue(row, last) {
    if (!row) return NaN;
    const sc = SCALES.poverty;
    let v = toNumber(row[row[sc.column] === undefined && sc.caColumn ? sc.caColumn : sc.column]);
    for (const c of [UK_POV, EU_POV, "Poverty rate (all ages)", "Poverty rate or stand-in", "Poverty rate (region, all ages)", "Child low-income rate (estimated from its province)", "Unemployment rate (stand-in for poverty)", "Low-income rate of the surrounding area (children 0-17)"])
      if (isNaN(v) && row[c]) v = toNumber(row[c]);
    if (isNaN(v) && last && row["Unmet basic needs (NBI, 2010)"]) v = toNumber(row["Unmet basic needs (NBI, 2010)"]);
    if (isNaN(v) && last && row["Poverty by year"]) {
      const ys = String(row["Poverty by year"]).split(";").map((x) => x.trim().split(":")).filter((x) => x.length === 2).sort((a, b) => a[0].localeCompare(b[0]));
      if (ys.length) v = toNumber(ys[ys.length - 1][1]);
    }
    return v;
  }
  // Which country's places a place is ranked among (Saint-Pierre-et-Miquelon among the islands).
  const countryOf = (id) => { id = String(id || ""); return isCA(id) ? "CA" : isUK(id) ? "UK" : isIE(id) ? "IE" : isFR(id) ? "ISLE" : euOf(id) || "US"; };
  let rankPool = null;
  // A rank for a place whose data has none but whose map figure is known: where that figure falls among its
  // country's places (marked as estimated).
  function rankFallback(row, id) {
    const v = povValue(row, true);
    if (isNaN(v)) return "";
    if (!rankPool) {
      rankPool = {};
      Object.entries(lookup).forEach(([k, r]) => { const x = povValue(r); if (!isNaN(x) && !r.pseudo) (rankPool[countryOf(k)] = rankPool[countryOf(k)] || []).push(x); });
    }
    const pool = rankPool[countryOf(id)] || [];
    if (!pool.length) return "";
    const lo = pool.filter((x) => x < v).length, hi = pool.filter((x) => x <= v).length;
    return String(Math.round(((lo + hi) / 2) / pool.length * 100));
  }
  let localePool = null;
  // A locale for a place whose data has none: the most common one in its county (US), province or region.
  function localeFallback(row, id) {
    if (!row) return "";
    if (!localePool) {
      localePool = {};
      Object.entries(lookup).forEach(([k, r]) => {
        if (!r.Locale || r.pseudo) return;
        const key = `${countryOf(k)}|${r.County || r.Province || r.Region || ""}`;
        localePool[key] = localePool[key] || {}; localePool[key][r.Locale] = (localePool[key][r.Locale] || 0) + 1;
      });
    }
    const m = localePool[`${countryOf(id)}|${row.County || row.Province || row.Region || ""}`];
    return m ? Object.entries(m).sort((a, b) => b[1] - a[1])[0][0] : "";
  }

  // Meetings found, as the meetings colouring counts them (the place's own records where CivicSearch has none).
  const meetOf = (r) => {
    let v = toNumber(r && r["Available Board Meetings"]);
    if (!(v > 0) && toNumber(r && r["Other Board Meetings"]) > 0) v = toNumber(r["Other Board Meetings"]);
    return isNaN(v) ? 0 : v;
  };
  // An enrollment of 0 that is a real figure (a place with no school and no school-age children, such as Sandstone,
  // WA), as opposed to the 0 some files use for "none reported": it has its own Enrollment year saying so.
  const realZero = (r) => !!r && String(r.Enrollment ?? "").trim() === "0" && !!r["Enrollment year"];
  const TIERS = ((window.SITE_CONFIG && window.SITE_CONFIG.sizeTiers) || {}).tiers || [];
  const tierOf = (r) => {
    const e = toNumber(r && r.Enrollment);
    return e > 0 || realZero(r) ? TIERS.find((t) => e >= t.min && (t.max == null || e <= t.max)) || null : null;
  };
  const tierRange = (t) => (t.max == null ? `${t.min.toLocaleString()} or more` : `${t.min.toLocaleString()}–${t.max.toLocaleString()}`);
  let peerPool = null;
  const MIN_PEERS = 5;
  // Where a place's meetings fall among its country's places of the same size tier: the share of the others
  // with fewer meetings found. A tier with fewer than 5 other places (a country's one or two largest cities) is
  // widened into the next smaller tiers. Null without an enrollment figure.
  function peerInfo(row, id) {
    const t = tierOf(row);
    if (!t || !row || row.pseudo) return null;
    if (!peerPool) {
      peerPool = {};
      Object.entries(lookup).forEach(([k, r]) => { const tt = tierOf(r); if (tt && !r.pseudo) { const key = `${countryOf(k)}|${tt.name}`; (peerPool[key] = peerPool[key] || []).push(meetOf(r)); } });
    }
    let i = TIERS.indexOf(t), lo = i, pool = [...(peerPool[`${countryOf(id)}|${t.name}`] || [])];
    while (pool.length - 1 < MIN_PEERS && lo > 0) { lo--; pool = pool.concat(peerPool[`${countryOf(id)}|${TIERS[lo].name}`] || []); }
    const v = meetOf(row), others = pool.length - 1;
    if (others < 1) return null;
    const tier = lo === i ? t : { name: `${TIERS[lo].name} to ${t.name}`, min: TIERS[lo].min, max: t.max };
    return { pct: Math.round(100 * pool.filter((x) => x < v).length / others), others, tier };
  }
  // Months since the latest meeting found. A date with only a year counts from 1 July, and one with only a month
  // from the 15th (or from today, if that is sooner).
  function monthsSince(row) {
    const m = String((row && row["Latest meeting"]) || "").trim().match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/);
    if (!m) return NaN;
    const now = new Date();
    let d = new Date(+m[1], m[2] ? +m[2] - 1 : 6, m[3] ? +m[3] : m[2] ? 15 : 1);
    if (d > now) d = now;
    return (now - d) / (30.44 * 864e5);
  }
  // "2019: 3.1%; 2024: 2.4%" -> [[2019, 3.1], [2024, 2.4]], oldest first.
  function yearPairs(v) {
    return String(v || "").split(";").map((p) => p.split(":").map((x) => x && x.trim())).filter((p) => /^\d{4}$/.test(p[0]) && !isNaN(toNumber(p[1])))
      .map((p) => [+p[0], toNumber(p[1])]).sort((a, b) => a[0] - b[0]);
  }
  function povChange(row, col = "Poverty by year") {
    const y = yearPairs(row && row[col]);
    return y.length >= 2 ? { d: y[y.length - 1][1] - y[0][1], from: y[0][0], to: y[y.length - 1][0] } : null;
  }
  // A district split since its earliest year (Peru) also has its figures added up on the borders before the split;
  // its change over time and its figures for years before the split are taken from those.
  const earlyCol = (row, col) => (row && row[col + " (earlier borders)"] ? col + " (earlier borders)" : col);
  const earlyWho = (row) => String((row && row["Earlier borders"]) || "");
  function pctChange(row, col) {
    const y = yearPairs(row && row[col]).filter((p) => p[1] > 0);
    return y.length >= 2 ? { d: 100 * (y[y.length - 1][1] / y[0][1] - 1), from: y[0][0], to: y[y.length - 1][0] } : null;
  }
  function perYear(row) {
    if (!row) return null;
    let n = toNumber(row["Available Board Meetings"]);
    if (!(n > 0) && toNumber(row["Other Board Meetings"]) > 0) n = toNumber(row["Other Board Meetings"]);
    if (!(n > 0)) return { v: 0 };
    n += toNumber(row["Meetings before 2025 (YouTube)"]) > 0 ? toNumber(row["Meetings before 2025 (YouTube)"]) : 0;   // US: the years before CivicSearch's
    const y = yearPairs(row["Meetings by year"]).filter((p) => p[1] > 0);
    const first = y.length ? y[0][0] : (String(row["Latest meeting"] || "").match(/^(\d{4})/) || [])[1];
    if (!first) return null;
    const years = Math.max(1, (Date.now() - new Date(+first, 0, 1)) / (365.25 * 864e5));
    return { v: n / years, first: +first };
  }
  const agoText = (mo) => (mo < 1 ? "under a month ago" : mo < 24 ? `about ${Math.round(mo)} month${Math.round(mo) === 1 ? "" : "s"} ago` : `about ${Math.round(mo / 12)} years ago`);
  // Share of the pupils counted who are in public schools.
  const PRIV = "Private school enrollment (within its borders)";
  function publicShare(row) {
    if (!row) return NaN;
    const pub = toNumber(row["Public school enrollment"]);
    if (isNaN(pub)) return NaN;
    const priv = toNumber(row[PRIV]);
    const tot = !isNaN(priv) ? pub + priv : toNumber(row.Enrollment);
    return tot > 0 ? Math.min(100, (100 * pub) / tot) : NaN;
  }

  // "No estimates": which figures are estimates rather than the place's own published data, per colouring.
  // Poverty: a figure borrowed from a wider area or another place (its province, département, region, county,
  // the surrounding area, the country, or the place it was made from). Official small-area estimates (Chile,
  // the Philippines, Peru, Croatia's poverty map) are the place's own published figures, so they count as data.
  const POV_EST = /^No commune figure|^No child figure: INE|^Created in .* from|^Made from |Merged into .*shown with|Overall at-risk-of-poverty rate of the|national rate|^No consumption poverty estimate|^No estimate of its own|withheld .* shown instead|Special Geographic Area|leaves out this comune|publishes no low-income figures for reserves|all-ages poverty rate for .* County/;
  const povEstimated = (r) => !!r && (!!r._povEst || (r.pseudo && !r.own) ||
    (!!r["Welfare rate basis"] && !/^Its own/.test(r["Welfare rate basis"])) ||
    POV_EST.test(r["Poverty note"] || r["How poverty was calculated"] || r.Notes || ""));
  const enrollEstimated = (r) => !!r && (!!r["Enrollment estimated"] || /estimated/i.test(r["Enrollment year"] || ""));
  function isEstimate(metric, r, id) {
    if (!r) return false;
    if (metric === "poverty") return povEstimated(r);
    if (metric === "rank") return povEstimated(r) || !!r._rankEst || String(r["Poverty rank in country"] ?? "") === "";
    if (metric === "enrollment" || metric === "peers") return enrollEstimated(r);
    // the year maps: an estimated current figure standing in for a count ("No estimates" hides it)
    if ((metric === "enrYear" || metric === "pubYear") && enrollEstimated(r)) return !yearPairs(r[YEAR_COL[metric]]).length;
    if (metric === "public") return !!r["Enrollment estimated"] && !!r.pseudo;
    if (metric === "locale") return !r.Locale;   // borrowed from its area's other places
    if (metric === "density") return !!r.pseudo && /^FRA-REST-/.test(id);   // a département's smaller communes together
    return false;
  }
  const noEst = () => !!($("map-no-est") && $("map-no-est").checked);
  const EST_HIDDEN = "#d4d4d4";
  // "School boards only" (shown with the meetings colouring): places whose count is a council or parliament stand-in
  // (app.js's "Meeting body" column) count as 0, like places with no meetings found.
  const boardsOnly = () => ["meetings", "recency", "perYear"].includes(metricNow()) && !!($("map-boards-only") && $("map-boards-only").checked);
  const standIn = (row) => !!row && /^Stand-in/.test(String(row["Meeting body"] || ""));

  // The "Color by" choice. A browser restoring the page after a reload (or after dropping the tab to save memory)
  // can leave the menu with no option chosen; fall back to the poverty colouring instead of breaking the map.
  function metricNow() {
    const sel = $("map-metric");
    if (sel && (SCALES[sel.value] || sel.value === "locale")) return sel.value;
    if (sel) sel.value = "poverty";
    return "poverty";
  }

  // The figure the poverty map shows: the place's own rate, else its country's other measures and stand-ins.
  function povNow(row) {
    let v = povValue(row, true);
    if (!row) return v;
    if (isNaN(v) && row[UK_POV]) v = toNumber(row[UK_POV]);
    if (isNaN(v) && row[EU_POV]) v = toNumber(row[EU_POV]);
    if (isNaN(v) && row["Poverty rate (all ages)"]) v = toNumber(row["Poverty rate (all ages)"]);   // Chile, Colombia
    if (isNaN(v) && row["Poverty rate or stand-in"]) v = toNumber(row["Poverty rate or stand-in"]);
    if (isNaN(v) && row["Poverty rate (region, all ages)"]) v = toNumber(row["Poverty rate (region, all ages)"]);   // Ireland
    // Saint-Pierre-et-Miquelon has no poverty rate; its unemployment rate stands in.
    if (isNaN(v) && row["Unemployment rate (stand-in for poverty)"]) v = toNumber(row["Unemployment rate (stand-in for poverty)"]);
    return v;
  }

  // The "in a chosen year" maps: a place's figures by year are its "... by year" column (and, before a split, the
  // figures on its earlier borders), plus its current figure, at that figure's year, where that's newer: so a
  // country that publishes one year only still shows, from that year. A year with no figure of its own shows the
  // latest earlier one (the tooltip says which year it's from); years before the first figure have none.
  const THIS_YEAR = new Date().getFullYear();
  const yearOfText = (t) => { const m = String(t || "").match(/(?<!\d)(19[89]\d|20[0-4]\d)(?!\d)/); return m ? +m[1] : 0; };
  let rowDs = null;
  const dsQuality = new WeakMap();
  function dsYears(row, id) {   // the year of its country's poverty measure and most common enrollment year
    const sig = ((window.SiteData && window.SiteData.datasets) || []).reduce((t, d) => t + d.rows.length, 0);
    if (!rowDs || rowDs.sig !== sig) {   // again once more countries' rows have loaded
      rowDs = new WeakMap(); rowDs.sig = sig; rowDs.prefix = {};
      ((window.SiteData && window.SiteData.datasets) || []).forEach((d) => {
        if (d.combined) return;
        d.rows.forEach((r) => { if (!rowDs.has(r)) rowDs.set(r, d); });
        const p = d.rows[0] && String(d.rows[0]["District ID"] || "").split("-")[0];
        if (p && !d.state && !rowDs.prefix[p]) rowDs.prefix[p] = d;
      });
      yearCache = new WeakMap();
    }
    // a map-only part of a country (no row in the data): its country, from the start of its id
    const d = rowDs.get(row) || (id && rowDs.prefix[String(id).split("-")[0]]);
    if (!d || !window.SiteQuality) return {};
    if (!dsQuality.has(d)) { let q = {}; try { q = window.SiteQuality.quality(d) || {}; } catch (e) { /* no label */ } dsQuality.set(d, { pov: q.year || 0, enr: q.enrollYear || 0 }); }
    return dsQuality.get(d);
  }
  function nowPoint(row, metric, id) {
    if (!row) return null;
    if (metric === "enrYear" || metric === "pubYear") {
      const v = metric === "enrYear" ? toNumber(row.Enrollment) : publicShare(row);
      if (metric === "enrYear" ? !(v > 0) : isNaN(v)) return null;
      const y = (metric === "pubYear" && yearOfText(row["Public share source"])) || yearOfText(row["Enrollment year"]) || (metric === "pubYear" && yearPairs(row["Enrollment by year"]).map((p) => p[0]).pop()) || dsYears(row, id).enr;
      return y ? [y, v] : null;
    }
    if (metric === "povYear") {
      const v = povNow(row);
      if (isNaN(v)) return null;
      const y = yearOfText(row["Poverty year"]) || dsYears(row, id).pov;
      return y ? [y, v] : null;
    }
    return null;
  }
  let yearCache = new WeakMap();
  function yearPoints(row, metric, id) {
    if (!row) return { own: [], early: [] };
    let c = yearCache.get(row);
    if (!c) yearCache.set(row, (c = {}));
    if (c[metric]) return c[metric];
    const col = YEAR_COL[metric], own = yearPairs(row[col]), early = yearPairs(row[col + " (earlier borders)"]);
    const now = metric === "povYear" && own.length ? null : nowPoint(row, metric, id);   // a poverty series already ends with the current figure
    if (now && (!own.length || now[0] > own[own.length - 1][0])) own.push(now);
    return (c[metric] = { own, early });
  }
  // The figure for a year: { v, from } (from: the year it's from, when an earlier one stands in).
  function yearValue(row, metric, y, id) {
    const { own, early } = yearPoints(row, metric, id);
    const exact = own.find((p) => p[0] === y) || early.find((p) => p[0] === y);
    if (exact) return { v: exact[1], from: y };
    const before = (ps) => ps.filter((p) => p[0] < y).pop();
    const b = before(own) || before(early);
    return b ? { v: b[1], from: b[0] } : null;
  }
  function color(row, id) {
    const c = colorOf(row, id);
    return c !== NO_DATA && noEst() && isEstimate(metricNow(), row, id) ? EST_HIDDEN : c;
  }

  function colorOf(row, id) {
    const metric = metricNow(), sc = SCALES[metric];
    if (metric === "locale") return localeColor(row && !row.Locale ? { Locale: localeFallback(row, id) } : row);
    if (metric === "rank" && row && String(row[sc.column] ?? "") === "") { const k = rankFallback(row, id); if (k !== "") row = { [sc.column]: k }; }
    let v = row ? toNumber(row[row[sc.column] === undefined && sc.caColumn ? sc.caColumn : sc.column]) : NaN;
    if (metric === "poverty") v = povNow(row);
    // Where CivicSearch has none, the meetings map uses counts from the district's own sources.
    if (metric === "meetings" && row && !(v > 0) && toNumber(row["Other Board Meetings"]) > 0) v = toNumber(row["Other Board Meetings"]);
    if (metric === "meetings" && isNaN(v)) v = 0;   // no meetings found counts as 0
    if (metric === "meetings" && boardsOnly() && standIn(row)) v = 0;   // a stand-in isn't a school board's meetings
    if (metric === "enrollment" && !(v > 0) && !realZero(row)) return NO_DATA;
    if (metric === "density") v = densityFor(row, id);   // no figure (0 is only ever "none reported")
    if (metric === "peers") { const p = peerInfo(row, id); v = p ? p.pct : NaN; }
    if (metric === "recency") v = boardsOnly() && standIn(row) ? NaN : monthsSince(row);   // a stand-in's latest meeting isn't a school board's
    if (metric === "public") v = publicShare(row);
    if (metric === "change") { const c = povChange(row); v = c ? c.d : NaN; }
    if (metric === "changePub") { const c = povChange(row, earlyCol(row, "Public share by year")); v = c ? c.d : NaN; }
    if (YEAR_COL[metric] && metric !== "meetYear") { const q = yearValue(row, metric, selectedYear(), id); v = q ? q.v : NaN; }
    if (metric === "meetYear") {
      const y = selectedYear(), at = (col) => { const p = yearPairs(row && row[col]).find((q) => q[0] === y); return p ? p[1] : NaN; };
      v = at(YEAR_COL[metric]);
      if (isNaN(v)) v = at(YEAR_COL[metric] + " (earlier borders)");   // before a split: the district it was part of
    }
    // A place with meetings in other years, or none found at all, had none that year; one whose recordings carry no
    // dates can't be placed in a year (grey). A stand-in body counts as none when "school boards only" is ticked.
    if (metric === "meetYear" && isNaN(v)) v = row && row["Meetings by year"] ? 0 : (toNumber(row && row["Available Board Meetings"]) > 0 ? NaN : 0);
    if (metric === "meetYear" && boardsOnly() && standIn(row)) v = 0;
    if (metric === "changeEnr") { const c = pctChange(row, earlyCol(row, "Enrollment by year")); v = c ? c.d : NaN; }
    if (metric === "changePop") { const c = pctChange(row, earlyCol(row, "Population by year")); v = c ? c.d : NaN; }
    if (metric === "perYear") { const q = boardsOnly() && standIn(row) ? { v: 0 } : perYear(row); v = q ? q.v : NaN; }
    if (isNaN(v)) return NO_DATA;
    const s2 = (metric === "poverty" || metric === "povYear") && OWN_SCALE[euOf(id)] ? SCALES[OWN_SCALE[euOf(id)]] : sc;
    const i = s2.breaks.findIndex((b) => v < b);
    return s2.colors[i === -1 ? s2.colors.length - 1 : i];
  }

  // In a state's view (or the territories'), districts elsewhere are faded.
  function inView(geoid) {
    if (current && current.combined) return true;
    const fr = current && current.country === "FR";
    if (isFR(geoid) || fr) return isFR(geoid) && fr;   // Saint-Pierre-et-Miquelon's view fades everything else
    const eu = current && EU[current.country] ? current.country : null;
    // One state or region of these countries (Germany's states, the island regions).
    const sub = current && current.parent && EU[current.parent.country] && current.parent.groups;
    if (sub) { const r = rowFor(geoid); return euOf(geoid) === current.parent.country && !!r && r[current.groupCol || sub.column] === current.name; }
    if (euOf(geoid) || eu) return euOf(geoid) === eu;
    const ie = current && current.country === "IE";
    if (isIE(geoid) || ie) { const r = rowFor(geoid); return isIE(geoid) && ie && (!current.state || (!!r && r.Region === current.name)); }
    const uk = current && (current.country === "UK" || (current.parent && current.parent.country === "UK"));
    if (isUK(geoid) || uk) return isUK(geoid) && uk && (!current.state || geoid.startsWith(`UK-${current.state.split(":")[1]}`));
    const ca = current && (current.country === "CA" || (current.parent && current.parent.country === "CA"));
    if (isCA(geoid) !== !!ca) return false;   // the US and Canada views fade each other
    if (ca) return !current.state || geoid.startsWith(`CA-${current.state.split(":")[1]}-`);
    if (!current || !current.state) return true;
    if (current.state === "territories") return /^(60|66|69|72|78)/.test(geoid);
    return !fips[current.state] || geoid.startsWith(fips[current.state]);
  }

  // Countries the site doesn't cover: grey outlines only (data/map/world.json, Natural Earth).
  const isWorld = (f) => String(gid(f)).startsWith("W-");
  // On the dark map they're near the background, so they can't be taken for a country of small districts, whose
  // many outlines would otherwise grey it over: there each district's outline is its own colour, darker.
  // (Light or dark as the site is: theme.js, whose switch redraws the map.)
  const isDark = () => (window.SiteTheme ? window.SiteTheme.dark() : !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches));
  const WORLD_STYLES = { dark: { fillColor: "#2b2e33", fillOpacity: 0.9, color: "#6b7077", weight: 0.5 },
    light: { fillColor: "#cfcfcf", fillOpacity: 0.35, color: "#9a9a9a", weight: 0.5 } };
  const worldStyle = () => WORLD_STYLES[isDark() ? "dark" : "light"];
  // the fill's own colour, a third darker (hex colours; anything else gets a dark grey)
  const shade = (c) => {
    const m = /^#([0-9a-f]{6})$/i.exec(String(c));
    if (!m) return "#202226";
    const n = parseInt(m[1], 16), d = (v) => Math.round(v * 0.66).toString(16).padStart(2, "0");
    return "#" + d(n >> 16) + d((n >> 8) & 255) + d(n & 255);
  };
  const undefinedArea = (f) => /^School District Not Defined$/i.test(f.properties.NAME || "") || sharedLand(f);
  // Spain: land shared by several towns (Bardenas Reales, facerías, comunidades), part of no single municipality.
  // Ecuador: the zones whose canton is disputed (zonas no delimitadas).
  const sharedLand = (f) => /^(ES|EC)-SHARED-/.test(f.properties.id || "");

  // Older borders in the year views: a district split from another, or one that lost part of itself to a new one
  // ("Border changes": "2017: San Miguel was made from Juliaca"), was one district with it in the years before. In
  // those years its outline takes its own fill colour, and it is drawn under its neighbours (restyle), so the line
  // between the districts that were one disappears while their outer edge stays. A newer district drawn over the
  // older border of the place it came from (INSIDE, from extra_borders.geojson) is hidden then, so that border shows.
  function preSplit(row, y) {
    if (!row || !y || !row["Border changes"]) return false;
    const name = String(row.District);
    return String(row["Border changes"]).split(";").some((p) => {
      const m = p.trim().match(/^(\d{4}):\s*(.+?) was made from (.+)$/);
      return !!m && +m[1] > y && (m[2] === name || m[3].split(/, | and /).includes(name));
    });
  }
  const olderBorders = (feature) => !!YEAR_COL[metricNow()] && preSplit(rowFor(gid(feature)), selectedYear());

  // Detail: districts and municipalities as they are, or each coloured by its region's (state's, province's) or whole
  // country's figures added up, as in Compare (window.SiteCompare's areas). Shown so, the lines inside an area take
  // its colour and it reads as one; ranks and same-size comparisons, which are about single places, are left grey.
  const detailLevel = () => ($("map-detail") ? $("map-detail").value : "place");
  let areaIndex = null;
  function areaEntry(id) {
    const C = window.SiteCompare, lv = detailLevel();
    if (lv === "place" || !C || !C.areas) return null;
    const list = C.areas();
    if (!areaIndex || areaIndex.list !== list) {
      areaIndex = { region: {}, country: {}, byId: {}, prefix: {}, list };
      list.forEach((e) => {
        const k = e.id.split(":").length > 2 ? "region" : "country";
        areaIndex.byId[e.id] = e;
        e.rows.forEach((r) => { areaIndex[k][r["District ID"]] = e; });
        const p = k === "country" && e.rows[0] && String(e.rows[0]["District ID"] || "").split("-")[0];
        if (p && !areaIndex.prefix[p]) areaIndex.prefix[p] = e;
      });
    }
    const base = rowFor(id);
    const find = (k) => areaIndex[k][id] || (base && areaIndex[k][base["District ID"]]);
    let hit = find(lv) || (lv === "region" ? find("country") : null);   // a country with no regions: the whole country
    if (!hit && base && base.pseudo) {
      // A map-only part of a country (Canada's land outside every board, France's smaller communes): its province's
      // or region's area, else its country's.
      const c = areaIndex.prefix[String(id).split("-")[0]];
      const r = c && lv === "region" && areaIndex.byId[`${c.id}:${base.Province || base.Region || base.State || ""}`];
      hit = r || c || null;
    }
    return hit;
  }
  function shownRow(id) {
    const e = areaEntry(id);
    return e ? window.SiteCompare.rowOf(e) : rowFor(id);
  }

  // Shown by region or country, each area gets its border: the edges of the features where the area changes (or
  // the land ends), found from the borders each pair of neighbours shares, drawn as lines over the fills. Country
  // borders are drawn heavier than those between a country's regions.
  let outlineLayer = null, outlineKey = null, outer = null, outerLoading = null;
  const outlineCache = new WeakMap();
  // A layer's outer edge: from data/map/outlines.json (map_outlines.py) where its districts were simplified one by
  // one; TopoJSON layers' neighbours share their borders exactly, so there the edges no neighbour shares are it.
  function outlinesOf(name, l, lv, list) {
    const c = outlineCache.get(l);
    if (c && c.lv === lv && c.list === list) return c.lines;
    const seg = new Map();   // edge -> [area key, country key, count]
    l.eachLayer((x) => {
      const f = x.feature, g = f && f.geometry;
      if (!g || isWorld(f) || !/Polygon/.test(g.type) || (frSmall && /^FRA-REST-/.test(gid(f)))) return;
      const e = areaEntry(gid(f));
      if (!e) return;   // in no area (a map-only part of a country): its edges are its neighbours' or the outline's
      const key = e.id, ck = e.id.split(":").slice(0, 2).join(":");
      (g.type === "Polygon" ? [g.coordinates] : g.coordinates).forEach((poly) => poly.forEach((ring) => {
        for (let i = 1; i < ring.length; i++) {
          const a = ring[i - 1], b = ring[i], ka = a[0] + "," + a[1], kb = b[0] + "," + b[1];
          if (ka === kb) continue;
          const k = ka < kb ? ka + "|" + kb : kb + "|" + ka, s = seg.get(k);
          if (!s) seg.set(k, [key, ck, 1, a, b]);
          else { s[2]++; if (s[0] !== key) s[0] = "*"; if (s[1] !== ck) s[1] = "*"; }
        }
      }));
    });
    const lines = { region: [], country: [] };
    const own = outer && outer[name];
    seg.forEach(([k, ck, n, a, b]) => {
      const ll = [[a[1], a[0]], [b[1], b[0]]];
      if (n === 1 ? !own : ck === "*") lines.country.push(ll);
      else if (n > 1 && k === "*") lines.region.push(ll);
    });
    if (own) own.forEach((line) => lines.country.push(line.map(([x, y]) => [y, x])));
    outlineCache.set(l, { lv, list, lines });
    return lines;
  }
  // Thinner when zoomed out, where a country's regions are small.
  function outlineWeights() {
    if (!outlineLayer) return;
    const z = map.getZoom(), [r, c] = outlineLayer.getLayers();
    r.setStyle({ weight: z < 3 ? 0.35 : z < 5 ? 0.6 : 0.9, opacity: z < 3 ? 0.55 : 0.75 });
    c.setStyle({ weight: z < 3 ? 0.9 : 1.6, opacity: 0.95 });
  }
  function drawOutlines() {
    const lv = detailLevel();
    const C = window.SiteCompare, list = lv !== "place" && C && C.areas ? C.areas() : null;
    const shown = list ? Object.entries(layers).filter(([n, l]) => !["world", "islands", "canada-fn", "france-small"].includes(n) && map.hasLayer(l)) : [];
    const key = [lv, shown.length].concat(shown.map(([, l]) => L.stamp(l))).join(",");
    if (key === outlineKey && list === (outlineLayer && outlineLayer._list)) return;
    outlineKey = key;
    if (outlineLayer) { outlineLayer.remove(); outlineLayer = null; }
    if (!list) return;
    if (!outer) {
      outerLoading = outerLoading || fetch("data/map/outlines.json").then((r) => (r.ok ? r.json() : {})).catch(() => ({}))
        .then((o) => { outer = o; outlineKey = null; drawOutlines(); });
      return;
    }
    const ink = isDark() ? "#f2f2f2" : "#1d1d1d";
    const region = [], country = [];
    shown.forEach(([n, l]) => { const o = outlinesOf(n, l, lv, list); region.push(...o.region); country.push(...o.country); });
    outlineLayer = L.layerGroup([
      L.polyline(region, { renderer, color: ink, interactive: false }),
      L.polyline(country, { renderer, color: ink, interactive: false })
    ]).addTo(map);
    outlineWeights();
    outlineLayer._list = list;
  }

  function style(feature) {
    if (isWorld(feature)) return worldStyle();
    if (undefinedArea(feature)) return { fillColor: NO_DISTRICT, fillOpacity: 0.9, color: "#8a9a80", weight: 0.3, dashArray: "2 3" };
    // With France's small communes drawn, each département's group of them stays underneath, unseen but clickable
    // (the communes are drawn on top, so it answers only between them).
    if (frSmall && /^FRA-REST-/.test(gid(feature))) return { fillOpacity: 0, opacity: 0, interactive: true };
    const f = window.SiteFilters;
    let on = inView(gid(feature));
    if (on && f && f.active()) {
      const r = rowFor(gid(feature));
      on = !!r && f.test(r);
    }
    // opacity and interactive undo the hidden state above (setStyle keeps options it isn't given).
    const lvl = detailLevel() !== "place" && areaEntry(gid(feature));
    const fill = lvl && ["rank", "peers"].includes(metricNow()) ? NO_DATA : color(lvl ? shownRow(gid(feature)) : rowFor(gid(feature)), gid(feature)), op = on ? 0.85 : 0.35;
    // solid, so the lines inside an area (drawn over one another) don't show
    if (lvl) return { fillColor: fill, fillOpacity: on ? 1 : 0.35, opacity: on ? 1 : 0.35, color: fill, weight: 2, interactive: true };
    // a map-only part of a country (no row of the data, so in no area): no lines of its own either
    if (detailLevel() !== "place") return { fillColor: fill, fillOpacity: op, opacity: 0, interactive: true };   // a region or country, read as one
    if (olderBorders(feature) && feature.properties.INSIDE) return { fillColor: fill, fillOpacity: 0, opacity: 0, interactive: false };   // under the older border it came from, which shows alone
    if (olderBorders(feature)) return { fillColor: fill, fillOpacity: op, opacity: op, color: fill, weight: 1.2, interactive: true };
    return { fillColor: fill, fillOpacity: op, opacity: 1, color: isDark() ? shade(fill) : "#555", weight: on ? 0.4 : 0.2, interactive: true };
  }

  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function tip(feature) {
    if (isWorld(feature)) return `<div class="map-tip"><strong>${esc(feature.properties.NAME)}</strong>Not covered on this site yet</div>`;
    const ae = areaEntry(gid(feature));
    if (ae) {   // shown by region or country: its figures added up
      const a = shownRow(gid(feature)), place = rowFor(gid(feature));
      const v = (c, f) => (String(a[c] ?? "") === "" ? "" : `<br>${f}: ${esc(a[c])}`);
      const pc = Object.keys(a).find((k) => /poverty|low income/i.test(k) && /%$/.test(String(a[k])));
      return `<div class="map-tip"><strong>${esc(a.District)}</strong>${esc(ae.label || "")}` +
        (pc ? `<br>Poverty (average, weighted by population): ${esc(a[pc])}` : "") +
        `<br>Available board meetings: ${toNumber(a["Available Board Meetings"]).toLocaleString()}` +
        (toNumber(a.Enrollment) > 0 ? `<br>Enrollment: ${toNumber(a.Enrollment).toLocaleString()}` : "") +
        (toNumber(a.Population) > 0 ? `<br>Population: ${toNumber(a.Population).toLocaleString()}` : "") +
        v("People per km² (estimated)", "People per km²") + v("Locale", "Locale (where most of its people live)") +
        (place ? `<div class="tip-note">Pointing at ${esc(place.District)}; pick "Districts and municipalities" under Detail for its own figures.</div>` : "") + "</div>";
    }
    const r = rowFor(gid(feature));
    if (r && r.Province && isCA(gid(feature))) return caTip(r);   // Canada's boards (Peru has a Province column too)
    if (sharedLand(feature)) return /^EC-/.test(feature.properties.id)
      ? `<div class="map-tip"><strong>${esc(String(feature.properties.NAME).replace(/^Zone with no canton: /, ""))}</strong>A zone whose canton is disputed (zona no delimitada), part of no canton</div>`
      : `<div class="map-tip"><strong>${esc(String(feature.properties.NAME).replace(/^Shared land \(no municipality\): /, ""))}</strong>Land shared by several towns (a facería, comunidad or similar), part of no single municipality</div>`;
    if (undefinedArea(feature)) return `<div class="map-tip"><strong>No school district</strong>Area the Census leaves outside any district, mostly national parks and other federal land (e.g. Grand Canyon, Yellowstone) or water</div>`;
    if (!r) return `<div class="map-tip"><strong>${esc(feature.properties.NAME)}</strong>Available board meetings: 0<br>No poverty data for this district</div>`;
    const eu = euOf(r["District ID"] || gid(feature));   // map-only areas (France's smaller communes) have no District ID
    const place = eu === "ISLE" ? r.Status || "" : eu ? EU_NAMES[eu] : [r.County, r.State || r.Territory || r.Nation].filter(Boolean).join(", ");
    const ukPov = r[UK_POV] !== undefined;
    const pov = toNumber(r[ukPov ? UK_POV : eu ? povCol(eu) : "Percentage of Children Ages 5-17 in Poverty"]);
    const unemp = toNumber(r["Unemployment rate (stand-in for poverty)"]);
    const frKids = toNumber(r["Child poverty rate (département)"]);
    const iePov = toNumber(r["Poverty rate (region, all ages)"]), esEst = toNumber(r["Child low-income rate (estimated from its province)"]);
    const meet = toNumber(r["Available Board Meetings"]);
    const enr = toNumber(r.Enrollment);
    const note = [r["Map note"], r["Poverty note"], r["Locale note"], r.Notes || r["Poverty figures"], r["Meetings note"], r["Other meetings source"] && `Other meetings: ${r["Other meetings source"]}`].filter(Boolean).map((x) => String(x).replace(/\.\s*$/, "")).join(". ");
    return `<div class="map-tip"><strong>${esc(r.District)}${place ? `, ${esc(place)}` : ""}</strong>` +
      (!isNaN(esEst) ? `Child low-income rate: not published (small municipality)<br>Estimate from its province's smaller municipalities: ${esEst.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "ES" ? `Child low-income rate: not published (small municipality)<br>Poverty rate of its region (all ages, Eurostat): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "EC" ? `Consumption poverty: no estimate (outside the survey)<br>Poverty rate of the Galápagos province (2010, reported by BBC News in 2013): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "BR" ? `Poverty: no figure of its own (created in 2025, after the census)<br>Rate of Sorriso, which it was part of (2022): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "MX" ? `Poverty: no figure of its own (made after CONEVAL's 2020 figures)<br>Rate of ${esc((String(r["Poverty note"] || "").match(/^Made from (.+?) and/) || [, "the municipality it was part of"])[1])}, which it was part of (2020): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "IT" ? `Low-income filers: figure left out (too few filers)<br>Share for its province (filers with €10,000 or less, 2023): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) && eu === "FRA" ? `Commune poverty rate: not published<br>Poverty rate of the whole département (all ages): ${iePov.toFixed(1)}%<br>`
        : !isNaN(iePov) ? `Poverty rate (all ages, its region): ${iePov.toFixed(1)}%<br>Unemployment (Census 2022): ${esc(r["Unemployment rate (Census 2022)"] || "–")}<br>`
        : isNaN(pov) && !isNaN(unemp) ? `Unemployment (stand-in for poverty): ${unemp.toFixed(1)}% (2015 est.)<br>`
        : `${ukPov ? "Children under 16 in low income" : eu === "ISLE" ? esc(r["Poverty measure"] || "Poverty") : ALL_AGES.has(eu) ? `Poverty (${eu === "LKA" ? "all ages, 2019" : eu === "RWA" ? "all ages, 2023/24" : eu === "CZE" ? "stand-in: unemployed per 100 residents aged 15–64, latest December" : eu === "PRY" ? "all ages, 2022" : eu === "IDN" ? "all ages, 2020" : eu === "MYS" ? "households below the poverty line, 2024" : eu === "PH" ? "all ages, 2021" : eu === "ARG" ? "all ages, its surveyed cities, first half of 2026" : eu === "ISR" ? "stand-in: people known to social services per 100 residents, 2019" : eu === "SVN" ? "stand-in: family and social benefits as a share of net income, 2024" : eu === "TWN" ? "stand-in: low- and middle-low-income people per 100 residents, 2026" : eu === "URY" ? "stand-in: Tarjeta Uruguay Social cards per 100 residents, 2024" : eu === "CRI" ? "stand-in: multidimensional poverty index × 100, 2023" : eu === "LTU" ? "all ages, at-risk-of-poverty rate, 2026" : eu === "IND" ? "all ages, multidimensional, 2019-21" : eu === "ZAF" ? "stand-in: public-school learners in quintile 1–3 (no-fee) schools, 2023" : eu === "GEO" ? "stand-in: families on the subsistence allowance per 100 residents, 2025" : eu === "KOR" ? "stand-in: Basic Livelihood Security recipients per 100 residents, 2025" : eu === "HR" ? "all ages, 2011 poverty map" : eu === "EE" ? "stand-in: subsistence-benefit applications per 100 residents a month, 2025" : eu === "AU" ? "stand-in: working-age income support per 100 people aged 15–64, 2026" : eu === "BE" ? "stand-in: integration income recipients per 100 inhabitants, 2025" : eu === "PT" ? "stand-in: minimum-income (RSI) recipients per 100 of working age, 2025" : eu === "JP" ? "welfare recipients, all ages, FY2024" : eu === "IT" ? "stand-in: filers with income of €10,000 or less, 2023" : eu === "FRA" ? "all ages, 60% of median, 2023" : eu === "EC" ? "all ages, consumption, 2014 estimate" : eu === "CL" ? "all ages, income, 2024" : eu === "BR" ? "all ages, income up to ½ minimum wage per person, 2022" : eu === "PE" ? "all ages, monetary, 2018" : eu === "MX" ? "all ages, multidimensional, 2020" : "all ages, multidimensional, 2018"})` : eu ? `Children in low income (${{ NO: "0–17, 2022–24", SE: "0–19, 2024", FI: "under 18", DK: "0–17, 50% line, 2024", NL: "CBS, 2024", DE: "under 15 on SGB II benefits, 2023", NZ: "60% line, 2025", IS: "national rate", CH: "0–17 on social assistance", ES: "under 18, 60% line, 2024", CL: "all ages, income, 2024", CO: "all ages, multidimensional, 2018", PL: "0–17 on family benefit, 2024", LV: "stand-in: 0–17 on basic means-tested benefits, 2025", KEN: "0–17 below the poverty line, 2022" }[eu]})` : "Child poverty"}: ${isNaN(pov) ? "–" : pov.toFixed(1) + "%"}<br>`) +
      (!isNaN(frKids) ? `Children under 18 in poverty, whole département: ${frKids.toFixed(1)}%<br>` : "") +
      (isNaN(povValue(r)) && !isNaN(povValue(r, true)) ? `Shown on the map: ${povValue(r, true).toFixed(1)}% (${r["Unmet basic needs (NBI, 2010)"] ? "unmet basic needs, 2010" : `its latest earlier figure, ${String(r["Poverty by year"] || "").split(";").map((x) => x.trim().split(":")[0]).sort().pop()}`})<br>` : "") +
      `Available board meetings: ${isNaN(meet) ? "0 (no school board)" : meet.toLocaleString()}` +
      (standIn(r) ? ` (a stand-in: council or parliament meetings, not a school board's${boardsOnly() ? (metricNow() === "recency" ? "; left out with School boards only" : "; shown as 0 with School boards only") : ""})` : r["Meeting body"] ? " (school board or equivalent)" : "") +
      (toNumber(r["Meetings before 2025 (YouTube)"]) > 0 ? ` on CivicSearch since January 2025; ${toNumber(r["Meetings before 2025 (YouTube)"]).toLocaleString()} earlier on the board's YouTube channel` : "") +
      (toNumber(r["Other Board Meetings"]) > 0 ? `${r.State ? " on CivicSearch" : meet > 0 ? " recorded" : ""}; ${toNumber(r["Other Board Meetings"]).toLocaleString()} from ${r.State ? "other sources" : "the council's or board's own records"} (see note)` : "") +
      (!(meet > 0) && !(toNumber(r["Other Board Meetings"]) > 0) && !r.State && !isCA(gid(feature)) && eu && eu !== "JP" ? `<span class="tip-zero"> — none found on YouTube; the council may post on Facebook or its own website instead</span>` : "") + `<br>` +
      `Enrollment: ${isNaN(enr) ? "not reported" : enr.toLocaleString()}${r["Enrollment estimated"] ? " (estimated: school-age children, no count published)" : /estimated/i.test(r["Enrollment year"] || "") ? ` (${esc(r["Enrollment year"])})` : realZero(r) || (eu === "AU" && !/^2021 Census/.test(r["Enrollment year"] || "") && r["Enrollment year"]) ? ` (${esc(r["Enrollment year"])})` : ""}` + rankLine(r, gid(feature)) +
      peerLine(r, gid(feature)) +
      (r["Latest meeting"] ? `<br>Latest recorded meeting: ${esc(r["Latest meeting"])}${isNaN(monthsSince(r)) ? "" : ` (${agoText(monthsSince(r))})`}` : "") +
      ((q) => (q && q.first ? `<br>Meetings per year since the first found (${q.first}): ${q.v < 10 ? q.v.toFixed(1) : Math.round(q.v)}` : ""))(perYear(r)) +
      ((c) => (c ? `<br>Change in the poverty figure, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)} points` : ""))(povChange(r)) +
      ((c) => (c ? `<br>Change in enrollment, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)}%${earlyCol(r, "Enrollment by year") !== "Enrollment by year" ? ` (${esc(earlyWho(r))}, on the borders before the split)` : ""}` : ""))(pctChange(r, earlyCol(r, "Enrollment by year"))) +
      ((c) => (c ? `<br>Change in population, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)}%${earlyCol(r, "Population by year") !== "Population by year" ? ` (${esc(earlyWho(r))}, on the borders before the split)` : ""}` : ""))(pctChange(r, earlyCol(r, "Population by year"))) +
      ((m) => {   // the year maps: the figure shown, and its year where an earlier one stands in
        if (!YEAR_COL[m] || m === "meetYear") return "";
        const y = selectedYear(), q = yearValue(r, m, y, gid(feature));
        if (!q) return `<br>In ${y}: no figure`;
        const f = m === "enrYear" ? Math.round(q.v).toLocaleString() + " pupils" : q.v.toFixed(1) + "%";
        return `<br>${m === "povYear" ? "Poverty" : m === "enrYear" ? "Enrollment" : "Public schools' share"} in ${y}: ${f}${q.from !== y ? ` (latest figure, from ${q.from})` : ""}`;
      })(metricNow()) +
      (olderBorders(feature) && r["Earlier borders"] ? `<br>In ${selectedYear()}, ${esc(r["Earlier borders"])} were one district (before the split)` : "") +
      (r["Border changes"] ? `<br>Border changes: ${esc(String(r["Border changes"]).replace(/(^|; )(\d{4}): /g, "$1in $2, "))}` : "") +
      publicLine(r) +
      (r.Locale ? `<br>Locale${/^(UK|IE)-/.test(r["District ID"]) || eu ? " (estimated)" : ""}: ${esc(r.Locale)}`
        : localeFallback(r, gid(feature)) ? `<br>Locale (estimated from its area's other places): ${esc(localeFallback(r, gid(feature)))}` : "") +
      (!isNaN(densityFor(r, gid(feature))) ? `<br>People per km²${r["People per km² (estimated)"] ? " (estimated)" : " (from its population and border)"}: ${Math.round(densityFor(r, gid(feature))).toLocaleString()}` : "") +
      (note ? `<div class="tip-note">${esc(note)}</div>` : "") + "</div>";
  }

  // Clicking a place with no meetings found opens a note saying why (e.g. an island whose legislature
  // streams only on its own website); other places just zoom in.
  function clickNote(feature, latlng) {
    const r = rowFor(gid(feature));
    if (!r || isWorld(feature) || toNumber(r["Available Board Meetings"]) > 0 || toNumber(r["Other Board Meetings"]) > 0) return;
    const why = r["Meetings note"] || "No meetings were found for this one.";
    // After the click (and the zoom it starts), so the map's own click handling doesn't close it at once.
    setTimeout(() => L.popup({ maxWidth: 320, autoPan: false }).setLatLng(latlng)
      .setContent(`<div class="map-tip"><strong>${esc(r.District)}: no meetings found</strong>${esc(why).replace(/\.$/, "")}.</div>`).openOn(map), 400);
  }

  function caTip(r) {
    const pov = toNumber(r["Percentage of Children Ages 0-17 in Low Income"]);
    const meet = toNumber(r["Available Board Meetings"]);
    const note = [r["How poverty was calculated"], r["Meetings note"]].filter(Boolean).join(". ");
    return `<div class="map-tip"><strong>${esc(r.District)}, ${esc(r.Province)}</strong>` +
      (r.pseudo ? "Not a school board<br>" : `${esc(r["Board type"])} board<br>`) +
      `Children (0–17) in low income: ${isNaN(pov) ? "–" : pov.toFixed(1) + "%"}${r.pseudo && !r.own ? " (province-wide rate)" : ""}<br>` +
      (isNaN(pov) && r["Low-income rate of the surrounding area (children 0-17)"] ? `Surrounding area's rate (stand-in; none is published for reserves): ${esc(r["Low-income rate of the surrounding area (children 0-17)"])}<br>` : "") +
      `Board meetings found: ${isNaN(meet) ? 0 : meet.toLocaleString()}` +
      (toNumber(r.Enrollment) > 0 ? `<br>Enrollment: ${toNumber(r.Enrollment).toLocaleString()}${r["Enrollment estimated"] ? " (estimated: school-age children, no count published)" : ` (${esc(r["Enrollment year"])}${r["Enrollment note"] ? `; ${esc(r["Enrollment note"])}` : ""})`}` : "") +
      (!isNaN(densityFor(r, r["District ID"])) ? `<br>People per km² (2021 Census, ${/First Nation \(band/.test(r["Board type"] || "") ? "the reserve" : /Province-wide/.test(r.Locale || "") ? "the whole province or territory" : "inside its border"}): ${densityFor(r, r["District ID"]) < 10 ? densityFor(r, r["District ID"]).toFixed(1) : Math.round(densityFor(r, r["District ID"])).toLocaleString()}` : "") +
      peerLine(r, r["District ID"]) +
      (r["Latest meeting"] ? `<br>Latest recorded meeting: ${esc(r["Latest meeting"])}${isNaN(monthsSince(r)) ? "" : ` (${agoText(monthsSince(r))})`}` : "") +
      ((q) => (q && q.first ? `<br>Meetings per year since the first found (${q.first}): ${q.v < 10 ? q.v.toFixed(1) : Math.round(q.v)}` : ""))(perYear(r)) +
      ((c) => (c ? `<br>Change in the poverty figure, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)} points` : ""))(povChange(r)) +
      ((c) => (c ? `<br>Change in enrollment, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)}%` : ""))(pctChange(r, "Enrollment by year")) +
      ((c) => (c ? `<br>Change in population, ${c.from}–${c.to}: ${c.d > 0 ? "+" : ""}${c.d.toFixed(1)}%` : ""))(pctChange(r, "Population by year")) +
      (r.Locale ? `<br>Locale (estimated): ${esc(r.Locale)}${/whole province or territory/.test(r["How poverty was calculated"] || "") ? " (serves the whole province or territory: the locale where most of the province's children live)" : ""}` : "") + rankLine(r, r["District ID"]) +
      (note ? `<div class="tip-note">${esc(note)}</div>` : "") + "</div>";
  }

  const peerLine = (r, id) => {
    const p = peerInfo(r, id);
    return p ? `<br>Meetings vs. same-size places: more than ${p.pct}% of the ${p.others.toLocaleString()} other${p.others === 1 ? "" : "s"} in its country with ${tierRange(p.tier)} pupils (${p.tier.name})` : "";
  };
  const publicLine = (r) => {
    const v = publicShare(r);
    if (isNaN(v)) return "";
    const priv = toNumber(r[PRIV]);
    if (r["Public share source"]) return `<br>In public schools: ${Math.round(v)}% of pupils (${toNumber(r["Public school enrollment"]).toLocaleString()} public, ${priv.toLocaleString()} private; ${esc(r["Public share source"])})`;
    return `<br>In public schools: ${Math.round(v)}% of pupils` + (!isNaN(priv)
      ? ` (${toNumber(r["Public school enrollment"]).toLocaleString()} public; ${priv.toLocaleString()} at private schools inside its border, NCES 2021-22)`
      : ` (${toNumber(r["Public school enrollment"]).toLocaleString()} of ${toNumber(r.Enrollment).toLocaleString()})`);
  };
  const rankLine = (r, id) => (String(r["Poverty rank in country"] ?? "") === "" && id && rankFallback(r, id) !== ""
    ? `<br>Poverty rank in its country: ${rankFallback(r, id)} of 100 (100 = highest); estimated from the figure the map shows for it`
    : String(r["Poverty rank in country"] ?? "") !== ""
    ? `<br>Poverty rank in its country: ${esc(r["Poverty rank in country"])} of 100 (100 = highest)${r._rankEst ? (r.pseudo && r.Province ? "; estimated: where its rate falls among the country's boards" : r["Child low-income rate (estimated from its province)"] ? "; estimated: where its province's estimate falls among Spain's municipalities" : r["Poverty rate (region, all ages)"] ? "; estimated from its region's rate" : "; estimated from the places in its region that have a figure") : ""}` : "");

  const ukView = () => current && (current.country === "UK" || (current.parent && current.parent.country === "UK"));

  function legend() {
    const sc = SCALES[metricNow()];
    const items = metricNow() === "locale"
      // Every kind, not just the current view's: the map also draws the neighbouring countries.
      ? [...LOCALES.filter((g) => !g.hide).map((g) => `<span><i style="background:${g.color}"></i>${g.label}</span>`),
        `<span><i style="background:${NO_DATA}"></i>No locale</span>`,
        `<span class="map-faded">Locale: the US uses NCES's locale codes and Canada Statistics Canada's population centre sizes; elsewhere it's estimated from population density (see the By locale tab)</span>`]
      : sc.labels.map((l, i) => `<span><i style="background:${sc.colors[i]}"></i>${l}</span>`);
    if (boardsOnly()) items.push(`<span class="map-faded">School boards only: places whose only meetings are a stand-in (town council or parliament, not a school board or its equivalent) ${metricNow() === "recency" ? "show as having no meeting found" : "show 0"}</span>`);
    if ($("map-boards-wrap")) $("map-boards-wrap").hidden = !["meetings", "recency", "perYear"].includes(metricNow());
    const jpv = current && current.country === "JP";
    const own = current && OWN_SCALE[current.country];
    if (own && metricNow() === "poverty") items.splice(0, items.length, ...SCALES[own].labels.map((l, i) => `<span><i style="background:${SCALES[own].colors[i]}"></i>${l}</span>`));
    if ((current && (current.country === "BE" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Belgium: people on the integration income (leefloon / revenu d'intégration) per 100 inhabitants, on its own scale${current.country === "BE" ? "" : " (under 0.5% to 6% or more)"}</span>`);
    if ((current && (current.country === "PT" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Portugal: people on the minimum-income benefit (RSI) per 100 of working age, on its own scale${current.country === "PT" ? "" : " (under 1% to 8% or more)"}</span>`);
    if ((current && (current.country === "LV" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Latvia: children on the basic means-tested benefits per 100 children, on its own scale${current.country === "LV" ? "" : " (under 1% to 8% or more)"}</span>`);
    if ((current && (current.country === "ISR" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Israel: a stand-in, people known to the local authority's social services in 2019 per 100 residents</span>`);
    if ((current && (current.country === "SVN" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Slovenia: family and social benefits as a share of residents' net income, on its own scale${current.country === "SVN" ? "" : " (under 3% to 8% or more)"}</span>`);
    if ((current && (current.country === "TWN" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Taiwan: people in low- and middle-low-income households per 100 residents, on its own scale${current.country === "TWN" ? "" : " (under 1% to 8% or more)"}</span>`);
    if ((current && (current.country === "URY" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Uruguay: Tarjeta Uruguay Social cards per 100 residents, on its own scale${current.country === "URY" ? "" : " (under 1% to 8% or more)"}</span>`);
    if ((current && (current.country === "ZAF" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">South Africa: public-school learners in quintile 1–3 (no-fee) schools, on its own scale${current.country === "ZAF" ? "" : " (under 25% to 97% or more)"}</span>`);
    if ((current && (current.country === "GEO" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Georgia: families on the subsistence allowance per 100 residents, on its own scale${current.country === "GEO" ? "" : " (under 8 to 24 or more)"}; Abkhazia and South Ossetia have no data</span>`);
    if ((current && (current.country === "KOR" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">South Korea: Basic Livelihood Security recipients per 100 residents, on its own scale${current.country === "KOR" ? "" : " (under 4% to 8% or more)"}</span>`);
    if ((current && (current.country === "CRI" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Costa Rica: UNDP's multidimensional poverty index × 100, on its own scale${current.country === "CRI" ? "" : " (under 3 to 15 or more)"}</span>`);
    if ((current && (current.country === "ARG" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Argentina: one figure per province, from its surveyed cities only</span>`);
    if ((current && (current.country === "EE" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Estonia: subsistence-benefit applications granted per 100 residents in an average month, on its own scale${current.country === "EE" ? "" : " (under 0.5% to 3% or more)"}</span>`);
    if ((jpv || (current && current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Japan: the welfare rate (people on public assistance), on its own scale${jpv ? "" : " (under 0.5% to 3% or more)"}; published for designated and core cities, and each prefecture's rate elsewhere</span>`);
    const ca = current && (current.country === "CA" || current.parent || current.combined);
    const euv = current && EU[current.country] ? current.country : null;
    if ((!ca || current.combined) && !(current && (current.country === "FR" || current.country === "IE" || euv)) && !ukView()) items.push(`<span><i style="background:${NO_DISTRICT}"></i>No school district (mostly national parks and federal land)</span>`);
    const faded = [];
    if (current && current.state) faded.push(current.state === "territories" ? "outside the U.S. territories" : `outside ${current.name}`);
    else if (ca && !current.combined) faded.push("outside Canada");
    if ((current && (current.country === "FR" || current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Saint-Pierre-et-Miquelon: unemployment rate (2015 est.) in place of child poverty, which isn't published there</span>`);
    if (euv === "ES" || (current && current.combined)) items.push(`<span><i style="background:${NO_DISTRICT}"></i>Spain: land shared by several towns, part of no municipality</span>`);
    if ((euv === "FRA" || (current && current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">France overseas: Guadeloupe, Martinique, French Guiana and Mayotte have no commune rates, so each commune shows its département's rate (INSEE; Guadeloupe, French Guiana and Mayotte from a 2017 survey)</span>`);
    if (euv === "EC" || (current && current.combined)) items.push(`<span><i style="background:${NO_DISTRICT}"></i>Ecuador: zones whose canton is disputed, part of no canton</span>`);
    if (euv === "FRA" || (current && current.combined)) items.push(`<span class="map-faded">France: communes too small for INSEE to publish a rate show their département's rate; tick “Smaller French communes” to draw each one</span>`);
    if (current && current.country === "FR") faded.push("outside Saint-Pierre-et-Miquelon");
    if (current && current.country === "IE") faded.push("outside Ireland");
    if (euv && !current.state) faded.push(`outside ${euv === "NL" ? "the Netherlands" : EU_NAMES[euv]}`);
    if ((euv || (current && current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">${euv === "ISLE" ? "Islands and microstates: the best figure available for each (child low income, the national poverty line or unemployment), not comparable with each other" : `${euv ? EU_NAMES[euv] : "Other countries"}: each country's own ${ALL_AGES.has(euv) ? "poverty measure (all ages)" : "child low-income measure"}, not comparable with each other or with the US rate`}</span>`);
    if (current && (current.country === "IE" || current.combined) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Ireland: overall poverty rate of each board's region (Eurostat), since no local or child rate is published</span>`);
    const ukv = current && (current.country === "UK" || (current.parent && current.parent.country === "UK"));
    if (ukv && !current.state) faded.push("outside the United Kingdom");
    if ((euv === "ES" || (current && current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">Spain: small municipalities with no child figure from INE show an estimate from their province's smaller municipalities that have one</span>`);
    if ((ukv || (current && current.combined)) && metricNow() === "poverty")
      items.push(`<span class="map-faded">UK: children under 16 in relative low income (DWP, 2024–25), not the same measure as the US or Canadian rates</span>`);
    if (ca && metricNow() === "poverty") items.push(`<span class="map-faded">${current.combined ? "Canadian boards" : "Canada"}: share of children 0–17 in low income (LIM-AT, 2020), not the same measure as the US child poverty rate</span>`);
    if (window.SiteFilters && window.SiteFilters.active()) faded.push("that don't match the filters");
    if ((euv === "ES" || (current && current.combined)) && metricNow() === "rank")
      items.push(`<span class="map-faded">Spain: small municipalities with no child figure are ranked by their province's estimate</span>`);
    if (metricNow() === "density")
      items.push(`<span><i style="background:${NO_DATA}"></i>No population figure</span>`,
        `<span class="map-faded">People per km²: each place's population over its land area (for US districts, the Census's 2024 population over the district's border); places under 100 are estimated rural, 100–499 mixed, 500–1,999 suburban and 2,000 or more urban</span>`);
    if (metricNow() === "enrollment")
      items.push(`<span><i style="background:${NO_DATA}"></i>No enrollment figure</span>`,
        `<span class="map-faded">Enrollment is counted differently from country to country (pupils at the place's schools, or pupils living there; some count only primary schools): see each view's note. Where no count is published, the figure is an estimate (school-age children living there), marked in the tooltip</span>`);
    if (metricNow() === "change")
      items.push(`<span><i style="background:${NO_DATA}"></i>Only one poverty year published</span>`,
        `<span class="map-faded">The change between the earliest and latest years in the place's Poverty by year column, in percentage points of its own measure. Only some countries publish more than one year (the US, the UK, Ireland, Germany, Italy, Poland, Spain, Belgium, Mexico, Chile, India, Indonesia, Kenya, Australia, the Philippines, Malaysia, Taiwan, Portugal, Czechia, the Baltic countries and others); the years and measures differ, so compare places within a country</span>`);
    if (YEAR_COL[metricNow()] && metricNow() !== "meetYear")
      items.push(`<span><i style="background:${NO_DATA}"></i>No figure for ${selectedYear() || "that year"}</span>`,
        `<span class="map-faded">${metricNow() === "povYear" ? "Each place's own poverty measure" : metricNow() === "enrYear" ? "Pupils, as each country counts them" : "Public schools' share of pupils"} in ${selectedYear() || "the chosen year"}: the figure for that year, else the latest one before it (a country that publishes one year shows from that year on). Pick the year above, or press Play to step through them</span>`);
    if (metricNow() === "changePub")
      items.push(`<span><i style="background:${NO_DATA}"></i>Only one year published</span>`,
        `<span class="map-faded">The change in public schools' share of pupils between the earliest and latest years given, in percentage points. So far for Portugal (2015–2024), Peru (2004–2025), Taiwan (2015–2025) and Indonesia (2021–2025)</span>`);
    if (["changeEnr", "changePop"].includes(metricNow()))
      items.push(`<span><i style="background:${NO_DATA}"></i>Only one year published</span>`,
        `<span class="map-faded">The change in ${metricNow() === "changeEnr" ? "enrollment" : "population"} between the earliest and latest years given, in percent. So far for ${metricNow() === "changeEnr" ? "the US, Japan, Colombia, Taiwan, Norway, Sweden, Denmark, the Netherlands, Portugal, Peru, Indonesia, Malaysia, Slovenia, South Korea, Lithuania and Georgia" : "33 countries, among them the US, most of Europe, the UK, Japan (census years), Mexico, Brazil, Colombia, Australia, Argentina, Chile, Indonesia and Paraguay (projections)"}</span>`);
    if (metricNow() === "meetYear")
      items.push(`<span><i style="background:${NO_DATA}"></i>Meetings found, but undated</span>`,
        `<span class="map-faded">Meetings recorded in ${selectedYear() || "the chosen year"}, from the dates in the recordings' titles (US districts: CivicSearch's monthly counts from January 2025, and before that the board's own YouTube channel). The current year is partial; press Play to step through the years</span>`);
    if (metricNow() === "perYear")
      items.push(`<span><i style="background:${NO_DATA}"></i>Meetings found, but no dates to count years from</span>`,
        `<span class="map-faded">Meetings found divided by the years since the first one found (from the recordings' dates), so a council that began posting recently isn't ranked below one with a long archive</span>`);
    if (metricNow() === "peers")
      items.push(`<span><i style="background:${NO_DATA}"></i>No enrollment figure (no size to compare by)</span>`,
        `<span class="map-faded">The share of places in the same country and the same size tier (by enrollment, as on the By district size tab: ${TIERS.map((t) => `${t.name} ${tierRange(t)}`).join(", ")}) that have fewer meetings found. Places with no meetings found are at 0%</span>`);
    if (metricNow() === "recency")
      items.push(`<span><i style="background:${NO_DATA}"></i>No meeting found (or no date for it)</span>`,
        `<span class="map-faded">Time since the latest meeting found. Some sources give only the year or month: those count from mid-year or mid-month</span>`);
    if (metricNow() === "public")
      items.push(`<span><i style="background:${NO_DATA}"></i>No public/private split published</span>`,
        `<span class="map-faded">Share of pupils in public schools. US districts: NCES public enrollment (2023) against private-school pupils inside the district's border (NCES Private School Survey 2021-22; secondary-only districts have no figure). Elsewhere: the public count against all pupils counted, where the source splits them</span>`);
    if (metricNow() === "rank")
      items.push(`<span class="map-faded">Rank within each country: where a place's poverty figure falls among its own country's places, so colours compare across countries even though the measures differ</span>`);
    // Places shown with no figure in this colouring (Svalbard and Pitcairn publish no poverty figure).
    if ((euv === "ISLE" || (current && current.combined)) && ["poverty", "rank"].includes(metricNow()) && Object.values(layers).some((l) => l.getLayers().some((f) => f.feature && !isWorld(f.feature) && !undefinedArea(f.feature) && style(f.feature).fillColor === NO_DATA)))
      items.push(`<span><i style="background:${NO_DATA}"></i>No figure published</span>`);
    if (noEst()) items.push(`<span><i style="background:${EST_HIDDEN}"></i>Estimate, hidden (“No estimates” is ticked): ${{
      poverty: "a rate borrowed from a wider area or another place", rank: "a rank from a borrowed or estimated rate",
      enrollment: "school-age children living there, where no count is published", peers: "its size group comes from an estimated enrollment",
      locale: "borrowed from its area's other places", density: "a French département's smaller communes taken together" }[metricNow()] || "none in this colouring"}</span>`);
    items.push(`<span><i style="background:${worldStyle().fillColor};border:1px solid ${worldStyle().color}"></i>Country not covered on this site</span>`);
    if (faded.length) items.push(`<span class="map-faded">Faded: districts ${faded.join(" or ")}</span>`);
    $("map-legend").innerHTML = items.join("");
  }

  // Islands are too small to see at a world zoom, so each also gets a dot (data/map/islands.json).
  let islandDots = [], spmLabel = null;
  // The year menu (shown with the "in a chosen year" colourings): the years the view's places have figures for.
  const selectedYear = () => +(($("map-year") && $("map-year").value) || 0);
  function fillYears() {
    const wrap = $("map-year-wrap"), sel = $("map-year"), col = YEAR_COL[metricNow()];
    if (!wrap) return;
    wrap.hidden = !col;
    if (!col) { stopPlay(); return; }
    const ys = new Set();
    const m = metricNow();
    if (m === "meetYear") ((current && current.rows) || []).forEach((r) => yearPairs(r[col]).forEach((p) => ys.add(p[0])));
    else ((current && current.rows) || []).forEach((r) => { const q = yearPoints(r, m); q.own.concat(q.early).forEach((p) => ys.add(p[0])); });
    if (col === "Meetings by year") [...ys].forEach((y) => { if (y < 2010) ys.delete(y); });   // a few stray early recordings
    if (ys.size) ys.add(THIS_YEAR);   // the latest figures, as they stand this year
    const list = [...ys].sort(), keep = selectedYear() || +(window.SiteLinks && window.SiteLinks.get("year")) || 0;
    sel.innerHTML = "";
    list.forEach((y) => sel.add(new Option(String(y), String(y))));
    if (!list.length) { sel.add(new Option("no years here", "")); return; }
    sel.value = String(list.includes(keep) ? keep : list[list.length - 1]);
  }
  let playing = null;
  function stopPlay() { if (playing) clearInterval(playing); playing = null; if ($("map-play")) { $("map-play").textContent = "▶ Play"; $("map-play").setAttribute("aria-pressed", "false"); } }
  function togglePlay() {
    if (playing) return stopPlay();
    const sel = $("map-year");
    if (sel.options.length < 2) return;
    if (sel.selectedIndex === sel.options.length - 1) sel.selectedIndex = 0;
    $("map-play").textContent = "❚❚ Pause"; $("map-play").setAttribute("aria-pressed", "true");
    restyle();
    playing = setInterval(() => {
      if (sel.selectedIndex >= sel.options.length - 1) return stopPlay();
      sel.selectedIndex += 1; sel.dispatchEvent(new Event("change"));
    }, 1300);
  }

  // Lighter borders when zoomed out, as map sites do: each zoom redraws every border from its points, and most of
  // them can't be told apart at a world or country zoom. Each border gets simplified copies (Douglas-Peucker, to
  // about two-thirds of a pixel at the band's closest zoom), made the first time they're needed; from zoom 6 the full
  // borders show, and from zoom 7 the detailed files (updateDetail). Swapped in before Leaflet projects the points.
  const LOD = [{ max: 3, tol: 0.12 }, { max: 5, tol: 0.03 }];
  const lodBand = (z) => { const i = LOD.findIndex((b) => z <= b.max); return i === -1 ? LOD.length : i; };
  let lodNow = null;
  function dpRing(pts, tol) {
    const n = pts.length;
    if (n <= 4) return pts;
    const keep = new Uint8Array(n), stack = [[0, n - 1]], t2 = tol * tol;
    keep[0] = keep[n - 1] = 1;
    while (stack.length) {
      const [a, b] = stack.pop();
      const ax = pts[a].lng, ay = pts[a].lat, dx = pts[b].lng - ax, dy = pts[b].lat - ay, l2 = dx * dx + dy * dy;
      let worst = -1, at = -1;
      for (let i = a + 1; i < b; i++) {
        let ex = pts[i].lng - ax, ey = pts[i].lat - ay;
        if (l2 > 0) { const t = Math.max(0, Math.min(1, (ex * dx + ey * dy) / l2)); ex -= t * dx; ey -= t * dy; }
        const d = ex * ex + ey * ey;
        if (d > worst) { worst = d; at = i; }
      }
      if (worst > t2) { keep[at] = 1; stack.push([a, at], [at, b]); }
    }
    const out = pts.filter((p, i) => keep[i]);
    if (out.length >= 3) return out;
    const k = Math.floor(n / 3);   // a place smaller than the tolerance: a triangle, so it still shows
    return [pts[0], pts[k], pts[2 * k]];
  }
  const lodOf = (ll, tol) => (ll.length && ll[0] && ll[0].lat !== undefined ? dpRing(ll, tol) : ll.map((x) => lodOf(x, tol)));
  function lodPath(l, band) {
    if (!l._latlngs || !l.feature) return;
    if (!l._lodFull) l._lodFull = l._latlngs;
    if (band >= LOD.length) { l._latlngs = l._lodFull; return; }
    const c = l._lod || (l._lod = []);
    l._latlngs = c[band] || (c[band] = lodOf(l._lodFull, LOD[band].tol));
  }
  function lodLayer(layer) { if (map && layer) { const b = lodBand(map.getZoom()); layer.eachLayer((l) => lodPath(l, b)); } }
  function lodAll() {
    const b = lodBand(map.getZoom());
    if (b === lodNow) return;
    lodNow = b;
    Object.values(layers).forEach((layer) => layer.eachLayer((l) => lodPath(l, b)));
  }

  function restyle() {
    // Saint-Pierre-et-Miquelon's label shows only in its own view.
    if (spmLabel) { if (current && current.country === "FR") spmLabel.addTo(map); else spmLabel.remove(); }
    Object.values(layers).forEach((l) => l.setStyle(style));
    // Districts that were still one in the chosen year go under their neighbours, whose outlines then draw the edge
    // (where the map's border of the older district still covers the newer one, as Juliaca's covers San Miguel's,
    // that older border shows alone). Otherwise a newer district goes back on top of the one it was made from.
    Object.values(layers).forEach((l) => l.eachLayer && l.eachLayer((x) => {
      const r = x.feature && x.bringToBack && rowFor(gid(x.feature));
      if (!r || !r["Border changes"]) return;
      if (olderBorders(x.feature)) x.bringToBack();
      else if (new RegExp(`(^|; )\\d{4}: ${String(r.District).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")} was made from `).test(r["Border changes"])) x.bringToFront();
    }));
    islandDots.forEach(({ dot, f }) => { const st = style(f); dot.setStyle({ fillColor: st.fillColor, fillOpacity: st.fillOpacity, opacity: st.fillOpacity }); });
    drawOutlines();
    legend();
  }

  // France's 29,500 small communes: drawn only when "Smaller French communes" is ticked (they're loaded then), in
  // place of each département's single map-only area.
  let frSmall = false, frSmallLoading = null, makeLayer = null;
  function setFrSmall(on) {
    if (on === undefined) on = !!($("map-fr-small") && $("map-fr-small").checked);
    if ($("map-fr-small")) $("map-fr-small").checked = on;
    if (!on) {
      frSmall = false;
      if (layers["france-small"]) layers["france-small"].remove();
      restyle();
      return Promise.resolve();
    }
    if (!frSmallLoading) {
      $("map-status").textContent = "Loading France's smaller communes…";
      frSmallLoading = fetch("data/map/france-small.json").then((r) => r.json()).then((fc) => {
        layers["france-small"] = makeLayer(fc);
        lodLayer(layers["france-small"]);
        layers["france-small"].eachLayer((l) => { const g = byId.get(gid(l.feature)); if (g && !g.layers.includes(l)) g.layers.push(l); });
        $("map-status").textContent = "";
      });
    }
    return frSmallLoading.then(() => {
      if (!$("map-fr-small").checked) return;
      frSmall = true;
      layers["france-small"].addTo(map);
      restyle();
    });
  }

  function setSecondary() {
    [["scsd", "map-secondary"], ["canada2", "map-canada-overlap"]].forEach(([n, box]) => {
      const l = layers[n];
      if (!l || !$(box)) return;
      if ($(box).checked) l.addTo(map); else l.remove();
    });
  }

  let userMoved = false, atUsed = false;
  function saveAt() {
    if (!userMoved || !window.SiteLinks) return;
    userMoved = false;
    const c = map.getCenter();
    window.SiteLinks.set({ at: `${c.lat.toFixed(3)},${c.lng.toFixed(3)},${map.getZoom()}` });
  }

  // Zooms to the selected state (or, for the territories, the first territory).
  function zoomToCurrent() {
    if (!map || !current) return;
    if (current.state === "territories") return jump("Puerto Rico");
    if (current.combined) return jump("United States and Canada");
    if (current.country === "FR") return jump("Saint-Pierre-et-Miquelon");
    if (current.country === "IE" && !current.state) return jump("Ireland");
    const euc = EU[current.country] ? current.country : null;
    if ((euc && (euc === "ISLE" || current.parent)) || current.country === "IE") {
      let b = null;
      layers[euc ? EU[euc] : "ireland"] && layers[euc ? EU[euc] : "ireland"].eachLayer((f) => {
        if (inView(gid(f.feature))) b = b ? b.extend(f.getBounds()) : L.latLngBounds(f.getBounds().getSouthWest(), f.getBounds().getNorthEast());
      });
      if (b) { map.fitBounds(b, { padding: [10, 10] }); $("map-jump").value = ""; }
      return;
    }
    if (EU_NAMES[current.country]) return jump(EU_NAMES[current.country]);
    if (current.country === "CA" && !current.parent) return jump("Canada");
    if (current.country === "UK" && !current.parent) return jump("United Kingdom");
    if (current.parent) {
      const uk = current.parent.country === "UK";
      const pre = uk ? `UK-${current.state.split(":")[1]}` : `CA-${current.state.split(":")[1]}-`;
      let b = null;
      (uk ? ["uk"] : ["canada", "canada2", "canada-fn"]).forEach((n) => layers[n] && layers[n].eachLayer((f) => {
        if (gid(f.feature).startsWith(pre)) b = b ? b.extend(f.getBounds()) : L.latLngBounds(f.getBounds().getSouthWest(), f.getBounds().getNorthEast());
      }));
      if (b) { map.fitBounds(b, { padding: [10, 10] }); $("map-jump").value = ""; }
      return;
    }
    const code = current.state && fips[current.state];
    if (!code) return jump("Contiguous US");
    let bounds = null;
    ["unsd", "elsd", "scsd"].forEach((n) => layers[n] && layers[n].eachLayer((f) => {
      if (f.feature.properties.GEOID.startsWith(code)) {
        bounds = bounds ? bounds.extend(f.getBounds()) : L.latLngBounds(f.getBounds().getSouthWest(), f.getBounds().getNorthEast());
      }
    }));
    if (current.state === "AK") return jump("Alaska");
    if (bounds) { map.fitBounds(bounds, { padding: [10, 10] }); $("map-jump").value = ""; }
  }

  function jump(name) {
    map.fitBounds(JUMPS[name]);
    $("map-jump").value = name;
  }


  // ---- Borders, loaded a country at a time --------------------------------------------------------
  // Each layer file is loaded when its country is the one shown or comes into view (data/map/index.json has each
  // file's bounding box), so a country's view doesn't hold every country's borders in memory.
  let index = null, renderer = null, dotRenderer = null;
  const loadingLayers = {};
  const toFC = (name, t) => (!t ? { type: "FeatureCollection", features: [] } : t.type === "FeatureCollection" ? t : topojson.feature(t, t.objects[name]));
  const SCHOOL_AGE = { ON: 0.139, AB: 0.156 };   // the share of people aged 5-17, 2021 Census
  function addLayer(name, t) {
    const files = { [name]: toFC(name, t) };
    if (name === "canada") {
      // Yukon and Nunavut have no public board of their own (the territory runs most schools), so
      // their territory-wide board shows in the main layer: the First Nation board, else the French one.
      // Areas outside every board (e.g. Ontario's Far North) are map-only: they get a row here from
      // their own properties, with the province-wide rate and 0 meetings, but no row in the data.
      const caNames = ((window.SITE_CONFIG.dataFiles.find((d) => d.country === "CA") || {}).groups || {}).names || {};
      // Their rank: where their rate falls among Canada's boards (marked as estimated).
      const caVals = Object.values(lookup).filter((r) => /^CA-/.test(r["District ID"] || "")).map((r) => toNumber(r["Percentage of Children Ages 0-17 in Low Income"])).filter((v) => !isNaN(v));
      const caRank = (v) => {
        v = toNumber(v); if (isNaN(v) || !caVals.length) return "";
        const lo = caVals.filter((x) => x < v).length, hi = caVals.filter((x) => x <= v).length;
        return String(Math.round(((lo + hi) / 2) / caVals.length * 100));
      };
      files.canada.features.filter((f) => f.properties.pseudo).forEach((f) => {
        const p = f.properties, prov = caNames[p.province] || p.province;
        lookup[gid(f)] = { District: `Rest of ${prov} (no school board)`, Province: prov, "Board type": "No school board", pseudo: true, own: !!p.own,
          Population: p.pop ?? "", "People per km² (estimated)": p.pop && p.land ? Math.round(10 * p.pop / p.land) / 10 : "",
          // No board counts its pupils: an estimate, its people times the province's share aged 5-17 (2021 Census,
          // about 13.9% in Ontario and 15.6% in Alberta; younger in the Far North's First Nations, so if anything low).
          // Its schools (First Nations', federal and provincial schools) are all publicly funded.
          ...(p.pop && SCHOOL_AGE[p.province] ? { Enrollment: Math.round(p.pop * SCHOOL_AGE[p.province]), "Enrollment estimated": "yes",
            "Enrollment year": "2021 Census (estimated: its people times the province's share aged 5–17)",
            "Public school enrollment": Math.round(p.pop * SCHOOL_AGE[p.province]) } : {}),
          Locale: "Rural",   // the Far North, national parks and reserves
          "Poverty rank in country": caRank(p.pct), _rankEst: caRank(p.pct) !== "",
          "Percentage of Children Ages 0-17 in Low Income": p.pct ?? "", "Available Board Meetings": 0,
          "How poverty was calculated": `Not a school board: the part of ${prov} outside every public board's border` +
            (p.province === "ON" ? ", mostly the Far North (unorganized land and First Nations reserves, whose schools are run by First Nations or small school authorities)"
              : p.province === "AB" ? ", mostly national parks (Wood Buffalo, Jasper, Banff) and First Nations reserves" : "") +
            (p.own ? `. Its rate is from the census areas inside it (${Number(p.kids).toLocaleString()} children; reserves have no low-income figures, so it mostly covers unorganized areas)`
              : `. Shown with ${prov}'s province-wide rate`) + `; 0 meetings. It isn't counted in ${prov}'s data` };
      });
      const caRows = files.canada.features.map((f) => lookup[gid(f)]).filter(Boolean);
      const hasMain = new Set(caRows.filter(caMainRow).map((r) => r.Province));
      const stand = {};
      caRows.filter((r) => !hasMain.has(r.Province)).forEach((r) => {
        const cur = stand[r.Province];
        if (!cur || (cur["Board type"] === "Francophone" && r["Board type"] !== "Francophone")) stand[r.Province] = r;
      });
      const caMain = (f) => { const r = lookup[gid(f)]; return caMainRow(r) || (!!r && stand[r.Province] === r); };
      files.canada2 = { type: "FeatureCollection", features: files.canada.features.filter((f) => !caMain(f)) };
      files.canada.features = files.canada.features.filter(caMain);
      layers.canada2 = makeLayer(files.canada2);
      if ($("map-canada-overlap") && $("map-canada-overlap").checked) layers.canada2.addTo(map);
      register("canada2");
    }
    if (name === "france") {
      // France: each département's communes with no published poverty rate, drawn together (map only), with the
      // département's rate.
      const frRank = {};   // each département's average commune rank, for the rank colours
      Object.values(lookup).forEach((r) => {
        if (!/^FRA-/.test(r["District ID"] || "") || String(r["Poverty rank in country"] ?? "") === "") return;
        const k = r.Region; frRank[k] = frRank[k] || [0, 0]; frRank[k][0] += Number(r["Poverty rank in country"]); frRank[k][1]++;
      });
      // Each département's smaller communes (rows of their own, with no commune poverty rate) added up for the group:
      // pupils in their schools, population by year, meetings found.
      const frSmallSum = {};
      Object.values(lookup).forEach((r) => {
        if (!/^FRA-/.test(r["District ID"] || "") || r.pseudo || String(r["Poverty rate (all ages)"] ?? "") !== "" || String(r["Poverty rate (region, all ages)"] ?? "") === "") return;
        const g = frSmallSum[r.Region] || (frSmallSum[r.Region] = { enr: 0, pub: 0, any: false, meet: 0, pop: {}, my: {}, n: 0 });
        g.n++;
        if (toNumber(r.Enrollment) > 0) { g.enr += toNumber(r.Enrollment); g.pub += toNumber(r["Public school enrollment"]) || 0; g.any = true; }
        g.meet += toNumber(r["Available Board Meetings"]) > 0 ? toNumber(r["Available Board Meetings"]) : 0;
        yearPairs(r["Meetings by year"]).forEach(([y, v]) => { g.my[y] = (g.my[y] || 0) + v; });
        yearPairs(r["Population by year"]).forEach(([y, v]) => { const q = g.pop[y] || (g.pop[y] = [0, 0]); q[0] += v; q[1]++; });
      });
      (files.france ? files.france.features : []).filter((f) => f.properties.pseudo).forEach((f) => {
        const p = f.properties, rk = frRank[p.dep], g = frSmallSum[p.dep];
        // population by year: the years every one of them has a figure for
        const popYears = g ? Object.entries(g.pop).filter(([, q]) => q[1] === g.n).map(([y, q]) => `${y}: ${q[0]}`).join("; ") : "";
        lookup[gid(f)] = { District: `Smaller communes of ${p.dep}`, Region: p.dep, pseudo: true, "Available Board Meetings": g ? g.meet : 0, Locale: "Rural",
          ...(g && g.any ? { Enrollment: g.enr, "Public school enrollment": g.pub, "Enrollment year": "2025-26 (nursery and primary schools; these communes' schools added up)" } : {}),
          ...(popYears ? { "Population by year": popYears } : {}),
          ...(g && Object.keys(g.my).length ? { "Meetings by year": Object.entries(g.my).map(([y, v]) => `${y}: ${v}`).join("; ") } : {}),
          Population: p.pop ?? "",   // its density: these communes' people over their land together
          "Poverty rate (all ages)": p.pct ?? "", "Child poverty rate (département)": p.child ?? "",
          "Poverty rank in country": rk ? String(Math.round(rk[0] / rk[1])) : "", _rankEst: !!rk,
          "Map note": `${Number(p.communes).toLocaleString()} communes (${Number(p.pop).toLocaleString()} people) that INSEE publishes no poverty rate for, as they have too few households; shown with ${p.dep}'s rate, and not counted in France's data` };
      });
    }
    const fc = files[name];
    // Puerto Rico's border is in the unified-district file; the other territories use the territory outlines.
    if (name === "territories") fc.features = fc.features.filter((f) => f.properties.GEOID !== "7200030");
    else if (!name.startsWith("canada")) fc.features = fc.features.filter((f) => !/^(60|66|69|78)/.test(String(f.properties.GEOID || "")));
    layers[name] = makeLayer(fc);
    lodLayer(layers[name]);
    if (name !== "scsd" || ($("map-secondary") && $("map-secondary").checked)) layers[name].addTo(map);
    // France's groups of small communes go underneath: their simplified borders overlap the larger communes' edges,
    // which should answer the mouse there.
    if (name === "france") layers.france.eachLayer((l) => { if (/^FRA-REST-/.test(gid(l.feature))) l.bringToBack(); });
    if (name === "islands") ISLANDS_DOTS();
    if (name === "spm") SPM_LABEL();
    areaById = null;
    if (name !== "world") register(name);
  }

  // The layer files a district's ID lives in.
  function layersForId(id) {
    id = String(id || "");
    const e = euOf(id);
    if (e) return [EU[e]];
    if (/^CA-/.test(id)) return ["canada", "canada-fn"];
    if (/^UK-/.test(id)) return ["uk"];
    if (/^IE-/.test(id)) return ["ireland"];
    if (/^FR-/.test(id)) return ["spm"];
    return ["unsd", "elsd", "scsd", "territories"];
  }
  // The layer files a data set's own view needs, whatever is on screen.
  function layersForView(ds) {
    if (!ds || ds.combined) return [];
    const c = ds.country || (ds.parent && ds.parent.country);
    if (!c) return ds.state === "territories" ? ["territories", "unsd"] : ["unsd", "elsd", "scsd", "territories"];
    return layersForId(`${c}-x`).concat(c === "CA" ? [] : []);
  }
  function loadLayers(names) {
    const todo = [...new Set(names)].filter((n) => n && n !== "world" && n !== "france-small" && n !== "canada2" && LAYERS.includes(n));
    const fresh = todo.filter((n) => !loadingLayers[n]);
    if (fresh.length) $("map-status").textContent = "Loading borders…";
    fresh.forEach((n) => {
      loadingLayers[n] = fetch(`data/map/${n}.json`).then((r) => (r.ok ? r.json() : null))
        .then((t) => { if (t) addLayer(n, t); }).catch((e) => console.error("map layer", n, e));
    });
    return Promise.all(todo.map((n) => loadingLayers[n])).then(() => {
      if (fresh.length) { $("map-status").textContent = ""; restyle(); setSecondary(); }
    });
  }
  // Loads the borders of every country now in view (a little beyond its edges).
  let viewReady = false;   // not before the first zoom to the data set: the map starts on the whole world
  // Each layer has a list of boxes (the 10-degree cells it has land in); an older index has one box.
  const boxes = (v) => (Array.isArray(v[0]) ? v : [v]);
  const layerInView = (n, b) => !!index[n] && boxes(index[n]).some((c) => L.latLngBounds([[c[1], c[0]], [c[3], c[2]]]).intersects(b));
  function ensureView() {
    if (!map || !index || !viewReady) return Promise.resolve();
    const b = map.getBounds().pad(0.2);
    return loadLayers(Object.keys(index).filter((n) => n[0] !== "_" && !loadingLayers[n] && layerInView(n, b))).then(updateDetail);
  }

  // Two levels of detail: the most detailed borders (index._hi) are drawn simplified when zoomed out, and swapped for
  // their full detail (<name>-hi.json) when zoomed in on them; zooming back out swaps the light ones back, freeing it.
  const HI_ZOOM = 7, LO_ZOOM = 6;
  const detail = {}, swapping = {};
  function updateDetail() {
    if (!map || !index || !index._hi || !viewReady) return;
    const z = map.getZoom(), b = map.getBounds();
    index._hi.forEach((n) => {
      if (!layers[n] || swapping[n]) return;
      const now = detail[n] || "lo";
      const want = z >= HI_ZOOM && layerInView(n, b) ? "hi" : z < LO_ZOOM || !layerInView(n, b.pad(0.5)) ? "lo" : now;
      if (want !== now) swapDetail(n, want);
    });
  }
  function swapDetail(n, level) {
    swapping[n] = true;
    if (level === "hi") $("map-status").textContent = "Loading detailed borders…";
    return fetch(`data/map/${n}${level === "hi" ? "-hi" : ""}.json`).then((r) => (r.ok ? r.json() : null)).then((t) => {
      swapping[n] = false;
      if ($("map-status").textContent === "Loading detailed borders…") $("map-status").textContent = "";
      if (!t) return;
      // The layer (and, for Canada, its overlapping boards) leaves the map and the search entries; the new one joins.
      const old = [layers[n]].concat(n === "canada" && layers.canada2 ? [layers.canada2] : []).filter(Boolean);
      const gone = new Set();
      old.forEach((o) => { o.eachLayer((l) => gone.add(l)); o.remove(); });
      byId.forEach((g) => { if (g.layers.some((l) => gone.has(l))) g.layers = g.layers.filter((l) => !gone.has(l)); });
      addLayer(n, t);
      detail[n] = level;
      drawOutlines();
      updateDetail();   // in case the view moved meanwhile
    }).catch((e) => { swapping[n] = false; console.error("map detail", n, e); });
  }

  function ISLANDS_DOTS() {
    layers.islands.eachLayer((l) => {
      // Countries across the date line (Fiji, Kiribati): centre on the largest island instead.
      let c = l.getBounds().getCenter();
      if (l.getBounds().getEast() - l.getBounds().getWest() > 180) {
        const g = l.feature.geometry, polys = g.type === "MultiPolygon" ? g.coordinates : [g.coordinates];
        const big = polys.reduce((a, p) => (p[0].length > a[0].length ? p : a));
        c = L.latLngBounds(big[0].map(([x, y]) => [y, x])).getCenter();
      }
      const dot = L.circleMarker(c, { renderer: dotRenderer, pane: "dots", radius: 5, weight: 1, color: "#333", fillOpacity: 0.85 }).addTo(map);
      dot.bindTooltip(() => tip(l.feature), { sticky: true });
      dot.on("click", (e) => { map.fitBounds(l.getBounds(), { maxZoom: 10 }); clickNote(l.feature, e.latlng); });
      islandDots.push({ dot, f: l.feature });
    });
    // Saint-Pierre-et-Miquelon is tiny and has no poverty figure, so a label keeps its meeting count visible.
  }
  function SPM_LABEL() {
    const spmRow = lookup["FR-SPM"];
    if (spmRow && layers.spm && layers.spm.getLayers().length) {
      const n = toNumber(spmRow["Available Board Meetings"]);
      spmLabel = L.marker(layers.spm.getBounds().getCenter(), { interactive: false, keyboard: false,
        icon: L.divIcon({ className: "map-label", html: `Saint-Pierre-et-Miquelon<br><b>${isNaN(n) ? 0 : n} meetings</b> (Territorial Council)`, iconSize: [190, 34], iconAnchor: [-14, 17] }) });
    }
  }

  function build(datasets, worldFile) {
    lookup = {};
    datasets.forEach((ds) => ds.rows.forEach((r) => {
      if (r["District ID"]) lookup[r["District ID"]] = r;
      if (r.State && r["District ID"]) fips[r.State] = r["District ID"].slice(0, 2);
    }));
    const tileUrl = () => `https://{s}.basemaps.cartocdn.com/${isDark() ? "dark_all" : "light_all"}/{z}/{x}/{y}{r}.png`;
    // One copy of the world: the map can't be dragged past its edges, and can't be zoomed out further than the world
    // fills the map (the minimum zoom follows the map's size).
    const WORLD = L.latLngBounds([[-85, -180], [85, 180]]);
    // Readers who ask their system for less motion get no zoom and pan animations.
    const calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    map = L.map("map", { preferCanvas: true, minZoom: 1, zoomSnap: 0.25, maxBounds: WORLD, maxBoundsViscosity: 1, worldCopyJump: false,
      zoomAnimation: !calm, fadeAnimation: !calm, markerZoomAnimation: !calm, keyboard: true })
      .setView([30, 0], 2);   // a view first: the island dots need one
    // before the canvas's own handlers (added with the first border), so the lighter borders are the ones projected
    map.on("viewreset zoomend", lodAll);
    const fitMinZoom = () => {
      const sz = map.getSize();
      const z = Math.max(1, Math.ceil(Math.log2(Math.max(sz.x, sz.y) / 256) * 4) / 4);
      // Zoom first, without animation (setMinZoom would zoom with one, which finishes after the zoom to the
      // country and undoes it).
      if (map.getZoom() < z) map.setZoom(z, { animate: false });
      map.setMinZoom(z);
    };
    fitMinZoom();
    map.on("resize", fitMinZoom);
    map.on("zoomend", () => outlineWeights());
    const tiles = L.tileLayer(tileUrl(), {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd", maxZoom: 14, noWrap: true, bounds: WORLD
    }).addTo(map);
    // The light/dark switch: the tiles, the grey countries, the outlines and the island dots follow it.
    if (window.SiteTheme) window.SiteTheme.onChange(() => { tiles.setUrl(tileUrl()); outlineKey = null; restyle(); });
    renderer = L.canvas({ padding: 0.3 });
    // Islands and small countries are circles drawn above every border (their own pane, over the canvas the
    // districts share), so a country loaded later never covers them. SVG, so the pane only catches the circles.
    map.createPane("dots").style.zIndex = 450;
    dotRenderer = L.svg({ pane: "dots", padding: 0.3 });
    makeLayer = (fc) => L.geoJSON(fc, {
      renderer, style,
      onEachFeature: (f, l) => {
        l.bindTooltip(() => tip(f), { sticky: true });
        l.on("click", (e) => { map.fitBounds(l.getBounds(), { maxZoom: 11 }); clickNote(f, e.latlng); });
        l.on("mouseover", () => l.setStyle({ weight: 2, color: "#111", opacity: 1 }));
        l.on("mouseout", () => l.setStyle(style(f)));
      }
    });
    addLayer("world", worldFile);

    const sel = $("map-jump");
    sel.add(new Option("—", ""));
    Object.keys(JUMPS).forEach((k) => sel.add(new Option(k, k)));
    sel.addEventListener("change", () => sel.value && jump(sel.value));
    $("map-metric").addEventListener("change", () => { fillYears(); restyle(); });
    if ($("map-detail")) {
      // The Detail slider (district, regional, national) sets the menu underneath, which links keep.
      const sel = $("map-detail"), range = $("map-detail-range"), LV = ["place", "region", "country"], WORD = ["District", "Regional", "National"];
      const sync = () => { if (!range) return; const i = Math.max(0, LV.indexOf(sel.value)); range.value = i; range.setAttribute("aria-valuetext", WORD[i]); };
      if (range) range.addEventListener("input", () => { sel.value = LV[+range.value]; sel.dispatchEvent(new Event("change")); });
      sel.addEventListener("change", () => { sync(); restyle(); });
      sync();
    }
    if ($("map-year")) $("map-year").addEventListener("change", restyle);
    if ($("map-play")) $("map-play").addEventListener("click", togglePlay);
    $("map-secondary").addEventListener("change", setSecondary);
    if ($("map-boards-only")) $("map-boards-only").addEventListener("change", restyle);
    if ($("map-fr-small")) $("map-fr-small").addEventListener("change", () => setFrSmall());
    if ($("map-canada-overlap")) $("map-canada-overlap").addEventListener("change", setSecondary);
    if ($("map-no-est")) $("map-no-est").addEventListener("change", restyle);
    legend();
    buildSearch();
  }

  // ---- "Find a district" --------------------------------------------------------------------
  // One entry per district in the data (its border may be several shapes, e.g. a Vermont union's
  // towns), plus entries for shapes whose own name differs (e.g. a Vermont town district).
  const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9 ]/g, " ").replace(/\bsaint\b/g, "st").replace(/\s+/g, " ");

  // Search entries come from the data (every district, loaded or not); a district's shapes join its entry when its
  // country's borders load (register), and picking one loads them first.
  const placeOf = (r) => (euOf(r["District ID"]) ? EU_NAMES[euOf(r["District ID"])] : [r.County, r.State || r.Territory || r.Province || r.Nation].filter(Boolean).join(", "));
  const entry = (id, r, extra) => ({ name: r.District, place: placeOf(r), layers: [], row: r, text: norm(`${r.District} ${placeOf(r)}`),
    size: Number(String(r.Enrollment || "").replace(/,/g, "")) || 0, ...extra });
  function register(n) {
    if (!layers[n]) return;
    layers[n].eachLayer((l) => {
      const p = l.feature.properties;
      if (undefinedArea(l.feature) || isWorld(l.feature)) return;
      const r = rowFor(gid(l.feature));
      const id = (r && r["District ID"]) || (r && r.District) || gid(l.feature);
      let g = byId.get(id);
      if (!g) {
        g = r ? entry(id, r, { scsd: n === "scsd" || n === "canada2" }) : { name: p.NAME, place: "", layers: [], row: r, text: norm(p.NAME), size: 0 };
        byId.set(id, g); searchIndex.push(g);
      }
      if (g.scsd === undefined) g.scsd = n === "scsd" || n === "canada2";
      if (((n !== "scsd" && n !== "canada2") || g.scsd) && !g.layers.includes(l)) g.layers.push(l);
      if (r && p.NAME && norm(p.NAME) !== norm(r.District) && n !== "scsd" && n !== "territories") {
        const sg = byId.get(`shape-${p.GEOID}`);
        if (sg) { if (!sg.layers.includes(l)) sg.layers.push(l); }
        else {
          const ng = { name: p.NAME, place: placeOf(r), layers: [l], row: r, partOf: r.District, text: norm(`${p.NAME} ${placeOf(r)}`), size: 0 };
          byId.set(`shape-${p.GEOID}`, ng); searchIndex.push(ng);
        }
      }
    });
  }

  function buildSearch() {
    byId = new Map(); searchIndex = [];
    Object.entries(lookup).forEach(([id, r]) => {
      if (!r || !r.District || byId.has(id)) return;
      const g = entry(id, r, /^FRA-\d/.test(id) ? { frSmall: true } : {});
      byId.set(id, g); searchIndex.push(g);
    });
    const box = $("map-search");
    box.addEventListener("input", showResults);
    box.addEventListener("keydown", (e) => {
      const items = [...$("map-results").children];
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((li, i) => li.setAttribute("aria-selected", String(i === active)));
        items[active].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        e.preventDefault();
        const pick = items[active >= 0 ? active : 0];
        if (pick) choose(Number(pick.dataset.i));
      } else if (e.key === "Escape") {
        hideResults();
      }
    });
    $("map-results").addEventListener("mousedown", (e) => {
      const li = e.target.closest("li[data-i]");
      if (li) { e.preventDefault(); choose(Number(li.dataset.i)); }
    });
    box.addEventListener("blur", () => setTimeout(hideResults, 150));
  }

  let shown = [];
  function showResults() {
    const q = norm($("map-search").value).trim();
    const list = $("map-results");
    active = -1;
    if (q.length < 2) return hideResults();
    const words = q.split(/\s+/);
    shown = searchIndex
      .filter((e) => words.every((w) => e.text.includes(w)))
      .sort((a, b) => (norm(b.name).startsWith(q) - norm(a.name).startsWith(q)) || (!!a.partOf - !!b.partOf) || b.size - a.size)
      .slice(0, 8);
    list.innerHTML = shown.length
      ? shown.map((e, i) => `<li role="option" data-i="${i}" aria-selected="false"><strong>${esc(e.name)}</strong>` +
          `<span>${esc([e.partOf ? `part of ${e.partOf}` : "", e.place].filter(Boolean).join(" · "))}</span></li>`).join("")
      : `<li class="map-results-none">No district found</li>`;
    list.hidden = false;
    $("map-search").setAttribute("aria-expanded", "true");
  }

  function hideResults() {
    $("map-results").hidden = true;
    $("map-search").setAttribute("aria-expanded", "false");
  }

  function choose(i) { focusEntry(shown[i]); }

  function focusEntry(e) {
    if (!e) return;
    const rid = e.row && e.row["District ID"];
    if (!e.layers.length && rid && !e._tried) { e._tried = true; return loadLayers(layersForId(rid)).then(() => focusEntry(e)); }
    if (e.frSmall && !e.layers.length) return setFrSmall(true).then(() => e.layers.length && focusEntry(e));
    if (!e.layers.length) { hideResults(); $("map-status").textContent = `${e.name} has no border on the map.`; return; }
    const id = e.row && e.row["District ID"];
    if (id && window.SiteLinks) window.SiteLinks.place(id);
    hideResults();
    $("map-search").value = e.name;
    [["scsd", "map-secondary"], ["canada2", "map-canada-overlap"]].forEach(([n, box]) => {
      if (e.layers.some((l) => layers[n] && layers[n].hasLayer(l)) && $(box) && !$(box).checked) {
        $(box).checked = true;
        setSecondary();
      }
    });
    let bounds = null;
    e.layers.forEach((l) => { bounds = bounds ? bounds.extend(l.getBounds()) : L.latLngBounds(l.getBounds().getSouthWest(), l.getBounds().getNorthEast()); });
    map.fitBounds(bounds, { maxZoom: 10, padding: [20, 20] });
    $("map-jump").value = "";
    if (highlight) highlight.remove();
    highlight = L.featureGroup(e.layers.map((l) => L.geoJSON(l.feature, { interactive: false,
      style: { fill: false, color: "#111", weight: 3 } }))).addTo(map);
    e.layers[0].openTooltip(bounds.getCenter());
  }

  window.SiteMap = {
    rowFor: (geoid) => rowFor(geoid),
    // For checking: the tooltip text of the first area whose ID starts with `prefix`.
    tipFor: (prefix) => {
      let t = "";
      Object.values(layers).forEach((l) => l.eachLayer((f) => { if (!t && f.feature && String(gid(f.feature)).startsWith(prefix)) t = tip(f.feature).replace(/<[^>]+>/g, " ").replace(/\s+/g, " "); }));
      return t;
    },
    // For checking: the areas drawn grey (no figure) in the current colouring, with their names.
    noData: () => {
      const out = [];
      Object.entries(layers).forEach(([n, l]) => l.eachLayer((f) => {
        const ft = f.feature;
        if (!ft || isWorld(ft) || undefinedArea(ft)) return;
        const id = gid(ft);
        if (colorOf(rowFor(id), id) === NO_DATA) out.push({ layer: n, id, name: (rowFor(id) || {}).District || ft.properties.NAME || "" });
      }));
      return out;
    },
    // For checking: areas whose tooltip doesn't show the figure their colour comes from, in the current colouring.
    tipGaps: () => {
      const metric = metricNow(), out = [];
      Object.entries(layers).forEach(([n, l]) => l.eachLayer((f) => {
        const ft = f.feature;
        if (!ft || isWorld(ft) || undefinedArea(ft)) return;
        const id = gid(ft), r = rowFor(id);
        if (!r) return;
        const text = tip(ft).replace(/<[^>]+>/g, " ");
        let want = null;
        if (metric === "poverty") { const v = povValue(r, true); if (!isNaN(v)) want = [v.toFixed(1), String(Math.round(v))]; }
        if (metric === "rank") { const k = String(r["Poverty rank in country"] ?? "") || rankFallback(r, id); if (k !== "") want = [`${k} of 100`]; }
        if (metric === "meetings") { const v = toNumber(r["Available Board Meetings"]); want = [isNaN(v) ? "0" : v.toLocaleString()]; }
        if (metric === "locale") { const v = r.Locale || localeFallback(r, id); if (v) want = [v]; }
        if (metric === "enrollment") { const v = toNumber(r.Enrollment); if (v > 0) want = [v.toLocaleString()]; }
        if (metric === "density") { const v = densityFor(r, id); if (!isNaN(v)) want = [Math.round(v).toLocaleString(), v.toFixed(1)]; }
        if (metric === "peers") { const p = peerInfo(r, id); if (p) want = [`more than ${p.pct}%`]; }
        if (metric === "recency") { const v = monthsSince(r); if (!isNaN(v)) want = [agoText(v)]; }
        if (metric === "public") { const v = publicShare(r); if (!isNaN(v)) want = [`${Math.round(v)}% of pupils`]; }
        if (want && !want.some((w) => text.includes(w))) out.push({ layer: n, id, name: r.District || "", want: want[0], text: text.replace(/\s+/g, " ").slice(0, 260) });
      }));
      return out;
    },
    // Areas greyed out by "No estimates" in the current colouring, for checking: {layer: count}.
    estHidden: () => {
      const out = {};
      Object.entries(layers).forEach(([n, l]) => l.eachLayer((f) => { if (f.feature && !isWorld(f.feature) && style(f.feature).fillColor === EST_HIDDEN) out[n] = (out[n] || 0) + 1; }));
      return out;
    },
    // Areas drawn grey (no figure) in the current colouring, for checking: [{layer, id, name}].
    grays: () => {
      const out = [];
      Object.entries(layers).forEach(([n, l]) => l.eachLayer((f) => {
        const ft = f.feature;
        if (!ft || isWorld(ft) || undefinedArea(ft)) return;
        if (style(ft).fillColor === NO_DATA) out.push({ layer: n, id: gid(ft), name: (rowFor(gid(ft)) || {}).District || ft.properties.NAME || "" });
      }));
      return out;
    },
    restyle: () => { if (map) restyle(); },
    // For checking: the border files loaded so far.
    loadedLayers: () => Object.keys(loadingLayers),
    detail: () => ({ ...detail }),
    position: () => map && { lat: +map.getCenter().lat.toFixed(3), lng: +map.getCenter().lng.toFixed(3), zoom: map.getZoom() },
    // Zooms to and outlines a district by its District ID (used by the site-wide search).
    focus: (id) => loading && loading.then(() => loadLayers(layersForId(id))).then(() => ((!byId.has(id) || !byId.get(id).layers.length) && /^FRA-/.test(id) ? setFrSmall(true) : null)).then(() => {
      map.invalidateSize(); focusEntry(byId.get(id) || [...byId.values()].find((g) => g.row && g.row["District ID"] === id));
    }),
    show(ds, datasets) {
      current = ds;
      if (!loading) {
        const get = (n) => fetch(`data/map/${n}.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
        loading = Promise.all([get("world"), get("aliases"), get("index")])
          .then(([world, al, idx]) => {
            aliases = al || {};
            // Without the index, every layer counts as everywhere: all load (the old behaviour).
            index = idx || Object.fromEntries(LAYERS.filter((n) => n !== "world").map((n) => [n, [[-180, -90, 180, 90]]]));
            build(datasets, world);
            map.on("moveend", () => { ensureView(); updateDetail(); saveAt(); });
            // Moves the reader makes (drag, wheel, pinch, the zoom buttons) go into the link as ?at=lat,lng,zoom.
            ["mousedown", "wheel", "touchstart", "keydown"].forEach((ev) => map.getContainer().addEventListener(ev, () => { userMoved = true; }, { passive: true }));
            $("map-status").textContent = "";
          })
          .catch((e) => { $("map-status").textContent = `Couldn't load the map (${e.message}).`; throw e; });
      }
      loading.then(() => loadLayers(layersForView(current))).then(() => {
        map.invalidateSize(); fillYears(); restyle();
        // A shared link's map position, the first time the map opens; otherwise the view's usual zoom.
        const at = !atUsed && window.SiteLinks && String(window.SiteLinks.get("at") || "").split(",").map(Number);
        atUsed = true;
        if (at && at.length === 3 && at.every(isFinite)) map.setView([at[0], at[1]], at[2]); else zoomToCurrent();
        // The zoom animates: load what's in view once it has settled (moveend does it after later moves too).
        setTimeout(() => { viewReady = true; ensureView(); }, 700);
      })
        .catch((e) => console.error("map:", e && e.stack));
    }
  };
})();
