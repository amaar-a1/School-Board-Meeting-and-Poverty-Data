// "Map" tab: school district borders (Census 2024 cartographic boundaries, in docs/data/map/)
// colored by the site's data. app.js calls SiteMap.show() when the tab or the data set changes.
(function () {
  const $ = (id) => document.getElementById(id);
  const LAYERS = ["world", "unsd", "elsd", "territories", "scsd", "canada", "spm", "uk", "ireland", "norway", "sweden", "finland", "denmark", "netherlands", "germany", "new-zealand", "islands", "iceland", "switzerland", "chile", "colombia", "brazil", "mexico", "peru"];   // files in data/map/; scsd only when ticked
  // Canadian boards overlap (public and Catholic, English and French). The main layer shows one
  // board per place; "canada2" holds the overlapping ones and shows when its box is ticked.
  // Quebec's French boards cover all of Quebec; elsewhere the public (or English) board does.
  // Quebec's Cree, Kativik and Littoral boards ("Special status") serve the north and east instead.
  const caMainRow = (r) => !!r && (r.pseudo || ["Public", "English public", "Special status"].includes(r["Board type"]) ||
    r["Board type"] === (r.Province === "Quebec" ? "French" : "English"));
  // The Nordic countries and the Netherlands: municipalities, IDs like "NO-0301" (map file per country).
  // Also Germany, New Zealand and the island countries ("ISLE-JAM"), which share the same handling.
  const EU = { NO: "norway", SE: "sweden", FI: "finland", DK: "denmark", NL: "netherlands", DE: "germany", NZ: "new-zealand", ISLE: "islands", IS: "iceland", CH: "switzerland", CL: "chile", CO: "colombia", MX: "mexico", BR: "brazil", PE: "peru" };
  const EU_NAMES = { NO: "Norway", SE: "Sweden", FI: "Finland", DK: "Denmark", NL: "Netherlands", DE: "Germany", NZ: "New Zealand", ISLE: "the islands and microstates", IS: "Iceland", CH: "Switzerland", CL: "Chile", CO: "Colombia", MX: "Mexico", BR: "Brazil", PE: "Peru" };
  const EU_POV = "Percentage of Children in Low Income";
  const povCol = (eu) => (eu === "ISLE" ? "Poverty rate or stand-in" : eu === "CL" || eu === "CO" || eu === "MX" || eu === "BR" || eu === "PE" ? "Poverty rate (all ages)" : EU_POV);
  const euOf = (id) => { const c = String(id).split("-")[0]; return String(id).includes("-") && EU[c] ? c : null; };
  const DRAW = ["world", "unsd", "elsd", "territories", "scsd", "canada", "canada2", "spm", "uk", "ireland", ...Object.values(EU)];
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
    Colombia: [[-4.3, -79.1], [12.6, -66.8]],
    "New Zealand": [[-47.4, 166.3], [-34.3, 178.7]],
    World: [[-58, -170], [75, 180]]
  };
  const SCALES = {
    poverty: {
      column: "Percentage of Children Ages 5-17 in Poverty",
      caColumn: "Percentage of Children Ages 0-17 in Low Income",   // Canada's measure (not the same as the US one)
      breaks: [10, 15, 20, 25, 30],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 10%", "10–15%", "15–20%", "20–25%", "25–30%", "30% or more"]
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
    }
  };
  const NO_DATA = "#9e9e9e";
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
      return { District: a.district, "Percentage of Children Ages 5-17 in Poverty": a.rate,
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
      Locale: rows[0].Locale
    };
  }

  const toNumber = (v) => {
    const s = String(v ?? "").trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  };

  function color(row) {
    const metric = $("map-metric").value, sc = SCALES[metric];
    let v = row ? toNumber(row[row[sc.column] === undefined && sc.caColumn ? sc.caColumn : sc.column]) : NaN;
    if (metric === "poverty" && row && isNaN(v) && row[UK_POV]) v = toNumber(row[UK_POV]);
    if (metric === "poverty" && row && isNaN(v) && row[EU_POV]) v = toNumber(row[EU_POV]);
    if (metric === "poverty" && row && isNaN(v) && row["Poverty rate (all ages)"]) v = toNumber(row["Poverty rate (all ages)"]);   // Chile, Colombia
    if (metric === "poverty" && row && isNaN(v) && row["Poverty rate or stand-in"]) v = toNumber(row["Poverty rate or stand-in"]);
    // Saint-Pierre-et-Miquelon has no poverty rate; its unemployment rate stands in.
    if (metric === "poverty" && row && isNaN(v) && row["Poverty rate (region, all ages)"]) v = toNumber(row["Poverty rate (region, all ages)"]);   // Ireland
    if (metric === "poverty" && row && isNaN(v) && row["Unemployment rate (stand-in for poverty)"]) v = toNumber(row["Unemployment rate (stand-in for poverty)"]);
    // Where CivicSearch has none, the meetings map uses counts from the district's own sources.
    if (metric === "meetings" && row && !(v > 0) && toNumber(row["Other Board Meetings"]) > 0) v = toNumber(row["Other Board Meetings"]);
    if (metric === "meetings" && isNaN(v)) v = 0;   // no meetings found counts as 0
    if (isNaN(v)) return NO_DATA;
    const i = sc.breaks.findIndex((b) => v < b);
    return sc.colors[i === -1 ? sc.colors.length - 1 : i];
  }

  // In a state's view (or the territories'), districts elsewhere are faded.
  function inView(geoid) {
    if (current && current.combined) return true;
    const fr = current && current.country === "FR";
    if (isFR(geoid) || fr) return isFR(geoid) && fr;   // Saint-Pierre-et-Miquelon's view fades everything else
    const eu = current && EU[current.country] ? current.country : null;
    // One state or region of these countries (Germany's states, the island regions).
    const sub = current && current.parent && EU[current.parent.country] && current.parent.groups;
    if (sub) { const r = rowFor(geoid); return euOf(geoid) === current.parent.country && !!r && r[sub.column] === current.name; }
    if (euOf(geoid) || eu) return euOf(geoid) === eu;
    const ie = current && current.country === "IE";
    if (isIE(geoid) || ie) return isIE(geoid) && ie;
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
  const WORLD_STYLE = { fillColor: "#cfcfcf", fillOpacity: 0.35, color: "#9a9a9a", weight: 0.5 };
  const undefinedArea = (f) => /^School District Not Defined$/i.test(f.properties.NAME || "");

  function style(feature) {
    if (isWorld(feature)) return WORLD_STYLE;
    if (undefinedArea(feature)) return { fillColor: NO_DISTRICT, fillOpacity: 0.9, color: "#8a9a80", weight: 0.3, dashArray: "2 3" };
    const f = window.SiteFilters;
    let on = inView(gid(feature));
    if (on && f && f.active()) {
      const r = rowFor(gid(feature));
      on = !!r && f.test(r);
    }
    return { fillColor: color(rowFor(gid(feature))), fillOpacity: on ? 0.85 : 0.35, color: "#555", weight: on ? 0.4 : 0.2 };
  }

  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function tip(feature) {
    if (isWorld(feature)) return `<div class="map-tip"><strong>${esc(feature.properties.NAME)}</strong>Not covered on this site yet</div>`;
    const r = rowFor(gid(feature));
    if (r && r.Province) return caTip(r);
    if (undefinedArea(feature)) return `<div class="map-tip"><strong>No school district</strong>Area the Census leaves outside any district, mostly national parks and other federal land (e.g. Grand Canyon, Yellowstone) or water</div>`;
    if (!r) return `<div class="map-tip"><strong>${esc(feature.properties.NAME)}</strong>Available board meetings: 0<br>No poverty data for this district</div>`;
    const eu = euOf(r["District ID"]);
    const place = eu === "ISLE" ? r.Status || "" : eu ? EU_NAMES[eu] : [r.County, r.State || r.Territory || r.Nation].filter(Boolean).join(", ");
    const ukPov = r[UK_POV] !== undefined;
    const pov = toNumber(r[ukPov ? UK_POV : eu ? povCol(eu) : "Percentage of Children Ages 5-17 in Poverty"]);
    const unemp = toNumber(r["Unemployment rate (stand-in for poverty)"]);
    const iePov = toNumber(r["Poverty rate (region, all ages)"]);
    const meet = toNumber(r["Available Board Meetings"]);
    const enr = toNumber(r.Enrollment);
    const note = [r["Map note"], r["Poverty note"], r.Notes || r["Poverty figures"], r["Meetings note"], r["Other meetings source"] && `Other meetings: ${r["Other meetings source"]}`].filter(Boolean).map((x) => String(x).replace(/\.\s*$/, "")).join(". ");
    return `<div class="map-tip"><strong>${esc(r.District)}${place ? `, ${esc(place)}` : ""}</strong>` +
      (!isNaN(iePov) ? `Poverty rate (all ages, its region): ${iePov.toFixed(1)}%<br>Unemployment (Census 2022): ${esc(r["Unemployment rate (Census 2022)"] || "–")}<br>`
        : isNaN(pov) && !isNaN(unemp) ? `Unemployment (stand-in for poverty): ${unemp.toFixed(1)}% (2015 est.)<br>`
        : `${ukPov ? "Children under 16 in low income" : eu === "ISLE" ? esc(r["Poverty measure"] || "Poverty") : eu === "CL" || eu === "CO" || eu === "MX" || eu === "BR" || eu === "PE" ? `Poverty (${eu === "CL" ? "all ages, income, 2024" : eu === "BR" ? "all ages, income up to ½ minimum wage per person, 2022" : eu === "PE" ? "all ages, monetary, 2018" : eu === "MX" ? "all ages, multidimensional, 2020" : "all ages, multidimensional, 2018"})` : eu ? `Children in low income (${{ NO: "0–17, 2022–24", SE: "0–19, 2024", FI: "under 18", DK: "0–17, 50% line, 2024", NL: "CBS, 2024", DE: "under 15 on SGB II benefits, 2023", NZ: "60% line, 2025", IS: "national rate", CH: "0–17 on social assistance", CL: "all ages, income, 2024", CO: "all ages, multidimensional, 2018" }[eu]})` : "Child poverty"}: ${isNaN(pov) ? "–" : pov.toFixed(1) + "%"}<br>`) +
      `Available board meetings: ${isNaN(meet) ? "0 (no school board)" : meet.toLocaleString()}` +
      (toNumber(r["Other Board Meetings"]) > 0 ? `${r.State ? " on CivicSearch" : meet > 0 ? " recorded" : ""}; ${toNumber(r["Other Board Meetings"]).toLocaleString()} from ${r.State ? "other sources" : "the council's or board's own records"} (see note)` : "") + `<br>` +
      `Enrollment: ${isNaN(enr) ? "not reported" : enr.toLocaleString()}` + rankLine(r) +
      (r["Latest meeting"] ? `<br>Latest recorded meeting: ${esc(r["Latest meeting"])}` : "") +
      (r.Locale ? `<br>Locale${/^(UK|IE)-/.test(r["District ID"]) || eu ? " (estimated)" : ""}: ${esc(r.Locale)}` : "") +
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
      `Board meetings found: ${isNaN(meet) ? 0 : meet.toLocaleString()}` +
      (toNumber(r.Enrollment) > 0 ? `<br>Enrollment: ${toNumber(r.Enrollment).toLocaleString()} (${esc(r["Enrollment year"])}${r["Enrollment note"] ? `; ${esc(r["Enrollment note"])}` : ""})` : "") +
      (r.Locale ? `<br>Locale (estimated): ${esc(r.Locale)}` : "") + rankLine(r) +
      (note ? `<div class="tip-note">${esc(note)}</div>` : "") + "</div>";
  }

  const rankLine = (r) => (String(r["Poverty rank in country"] ?? "") !== ""
    ? `<br>Poverty rank in its country: ${esc(r["Poverty rank in country"])} of 100 (100 = highest)` : "");

  const ukView = () => current && (current.country === "UK" || (current.parent && current.parent.country === "UK"));

  function legend() {
    const sc = SCALES[$("map-metric").value];
    const items = sc.labels.map((l, i) => `<span><i style="background:${sc.colors[i]}"></i>${l}</span>`);
    const ca = current && (current.country === "CA" || current.parent || current.combined);
    const euv = current && EU[current.country] ? current.country : null;
    if ((!ca || current.combined) && !(current && (current.country === "FR" || current.country === "IE" || euv)) && !ukView()) items.push(`<span><i style="background:${NO_DISTRICT}"></i>No school district (mostly national parks and federal land)</span>`);
    const faded = [];
    if (current && current.state) faded.push(current.state === "territories" ? "outside the U.S. territories" : `outside ${current.name}`);
    else if (ca && !current.combined) faded.push("outside Canada");
    if ((current && (current.country === "FR" || current.combined)) && $("map-metric").value === "poverty")
      items.push(`<span class="map-faded">Saint-Pierre-et-Miquelon: unemployment rate (2015 est.) in place of child poverty, which isn't published there</span>`);
    if (current && current.country === "FR") faded.push("outside Saint-Pierre-et-Miquelon");
    if (current && current.country === "IE") faded.push("outside Ireland");
    if (euv && !current.state) faded.push(`outside ${euv === "NL" ? "the Netherlands" : EU_NAMES[euv]}`);
    if ((euv || (current && current.combined)) && $("map-metric").value === "poverty")
      items.push(`<span class="map-faded">${euv === "ISLE" ? "Islands and microstates: the best figure available for each (child low income, the national poverty line or unemployment), not comparable with each other" : `${euv ? EU_NAMES[euv] : "Other countries"}: each country's own ${euv === "CL" || euv === "CO" || euv === "MX" || euv === "BR" || euv === "PE" ? "poverty measure (all ages)" : "child low-income measure"}, not comparable with each other or with the US rate`}</span>`);
    if (current && (current.country === "IE" || current.combined) && $("map-metric").value === "poverty")
      items.push(`<span class="map-faded">Ireland: overall poverty rate of each board's region (Eurostat), since no local or child rate is published</span>`);
    const ukv = current && (current.country === "UK" || (current.parent && current.parent.country === "UK"));
    if (ukv && !current.state) faded.push("outside the United Kingdom");
    if ((ukv || (current && current.combined)) && $("map-metric").value === "poverty")
      items.push(`<span class="map-faded">UK: children under 16 in relative low income (DWP, 2024–25), not the same measure as the US or Canadian rates</span>`);
    if (ca && $("map-metric").value === "poverty") items.push(`<span class="map-faded">${current.combined ? "Canadian boards" : "Canada"}: share of children 0–17 in low income (LIM-AT, 2020), not the same measure as the US child poverty rate</span>`);
    if (window.SiteFilters && window.SiteFilters.active()) faded.push("that don't match the filters");
    if ($("map-metric").value === "rank")
      items.push(`<span class="map-faded">Rank within each country: where a place's poverty figure falls among its own country's places, so colours compare across countries even though the measures differ</span>`);
    items.push(`<span><i style="background:${WORLD_STYLE.fillColor};border:1px solid ${WORLD_STYLE.color}"></i>Country not covered on this site</span>`);
    if (faded.length) items.push(`<span class="map-faded">Faded: districts ${faded.join(" or ")}</span>`);
    $("map-legend").innerHTML = items.join("");
  }

  // Islands are too small to see at a world zoom, so each also gets a dot (data/map/islands.json).
  let islandDots = [], spmLabel = null;
  function restyle() {
    // Saint-Pierre-et-Miquelon's label shows only in its own view.
    if (spmLabel) { if (current && current.country === "FR") spmLabel.addTo(map); else spmLabel.remove(); }
    Object.values(layers).forEach((l) => l.setStyle(style));
    islandDots.forEach(({ dot, f }) => { const st = style(f); dot.setStyle({ fillColor: st.fillColor, fillOpacity: st.fillOpacity, opacity: st.fillOpacity }); });
    legend();
  }

  function setSecondary() {
    [["scsd", "map-secondary"], ["canada2", "map-canada-overlap"]].forEach(([n, box]) => {
      const l = layers[n];
      if (!l || !$(box)) return;
      if ($(box).checked) l.addTo(map); else l.remove();
    });
  }

  // Zooms to the selected state (or, for the territories, the first territory).
  function zoomToCurrent() {
    if (!map || !current) return;
    if (current.state === "territories") return jump("Puerto Rico");
    if (current.combined) return jump("United States and Canada");
    if (current.country === "FR") return jump("Saint-Pierre-et-Miquelon");
    if (current.country === "IE") return jump("Ireland");
    const euc = EU[current.country] ? current.country : null;
    if (euc && (euc === "ISLE" || current.parent)) {
      let b = null;
      layers[EU[euc]] && layers[EU[euc]].eachLayer((f) => {
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
      (uk ? ["uk"] : ["canada", "canada2"]).forEach((n) => layers[n] && layers[n].eachLayer((f) => {
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

  function build(datasets, topo) {
    lookup = {};
    datasets.forEach((ds) => ds.rows.forEach((r) => {
      if (r["District ID"]) lookup[r["District ID"]] = r;
      if (r.State && r["District ID"]) fips[r.State] = r["District ID"].slice(0, 2);
    }));
    const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    map = L.map("map", { preferCanvas: true, minZoom: 2, zoomSnap: 0.25 }).setView([30, 0], 2);   // a view first: the island dots need one
    L.tileLayer(`https://{s}.basemaps.cartocdn.com/${dark ? "dark_all" : "light_all"}/{z}/{x}/{y}{r}.png`, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd", maxZoom: 14
    }).addTo(map);
    const renderer = L.canvas({ padding: 0.3 });
    const files = {};
    LAYERS.forEach((name, i) => {
      const t = topo[i];
      files[name] = !t ? { type: "FeatureCollection", features: [] } : t.type === "FeatureCollection" ? t : topojson.feature(t, t.objects[name]);
    });
    // Yukon and Nunavut have no public board of their own (the territory runs most schools), so
    // their territory-wide board shows in the main layer: the First Nation board, else the French one.
    // Areas outside every board (e.g. Ontario's Far North) are map-only: they get a row here from
    // their own properties, with the province-wide rate and 0 meetings, but no row in the data.
    const caNames = ((window.SITE_CONFIG.dataFiles.find((d) => d.country === "CA") || {}).groups || {}).names || {};
    files.canada.features.filter((f) => f.properties.pseudo).forEach((f) => {
      const p = f.properties, prov = caNames[p.province] || p.province;
      lookup[gid(f)] = { District: `Rest of ${prov} (no school board)`, Province: prov, "Board type": "No school board", pseudo: true, own: !!p.own,
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
    DRAW.forEach((name) => {
      const fc = files[name];
      // Puerto Rico's border is in the unified-district file; the other territories use the territory outlines.
      if (name === "territories") fc.features = fc.features.filter((f) => f.properties.GEOID !== "7200030");
      else if (!name.startsWith("canada")) fc.features = fc.features.filter((f) => !/^(60|66|69|78)/.test(f.properties.GEOID));
      layers[name] = L.geoJSON(fc, {
        renderer, style,
        onEachFeature: (f, l) => {
          l.bindTooltip(() => tip(f), { sticky: true });
          l.on("click", (e) => { map.fitBounds(l.getBounds(), { maxZoom: 11 }); clickNote(f, e.latlng); });
          l.on("mouseover", () => l.setStyle({ weight: 2, color: "#111" }));
          l.on("mouseout", () => l.setStyle(style(f)));
        }
      });
      if (name !== "scsd" && name !== "canada2") layers[name].addTo(map);
    });
    if (layers.islands) layers.islands.eachLayer((l) => {
      // Countries across the date line (Fiji, Kiribati): centre on the largest island instead.
      let c = l.getBounds().getCenter();
      if (l.getBounds().getEast() - l.getBounds().getWest() > 180) {
        const g = l.feature.geometry, polys = g.type === "MultiPolygon" ? g.coordinates : [g.coordinates];
        const big = polys.reduce((a, p) => (p[0].length > a[0].length ? p : a));
        c = L.latLngBounds(big[0].map(([x, y]) => [y, x])).getCenter();
      }
      const dot = L.circleMarker(c, { renderer, radius: 5, weight: 1, color: "#333", fillOpacity: 0.85 }).addTo(map);
      dot.bindTooltip(() => tip(l.feature), { sticky: true });
      dot.on("click", (e) => { map.fitBounds(l.getBounds(), { maxZoom: 10 }); clickNote(l.feature, e.latlng); });
      islandDots.push({ dot, f: l.feature });
    });
    // Saint-Pierre-et-Miquelon is tiny and has no poverty figure, so a label keeps its meeting count visible.
    const spmRow = lookup["FR-SPM"];
    if (spmRow && layers.spm && layers.spm.getLayers().length) {
      const n = toNumber(spmRow["Available Board Meetings"]);
      spmLabel = L.marker(layers.spm.getBounds().getCenter(), { interactive: false, keyboard: false,
        icon: L.divIcon({ className: "map-label", html: `Saint-Pierre-et-Miquelon<br><b>${isNaN(n) ? 0 : n} meetings</b> (Territorial Council)`, iconSize: [190, 34], iconAnchor: [-14, 17] }) });
    }
    const sel = $("map-jump");
    sel.add(new Option("—", ""));
    Object.keys(JUMPS).forEach((k) => sel.add(new Option(k, k)));
    sel.addEventListener("change", () => sel.value && jump(sel.value));
    $("map-metric").addEventListener("change", restyle);
    $("map-secondary").addEventListener("change", setSecondary);
    if ($("map-canada-overlap")) $("map-canada-overlap").addEventListener("change", setSecondary);
    legend();
    buildSearch();
  }

  // ---- "Find a district" --------------------------------------------------------------------
  // One entry per district in the data (its border may be several shapes, e.g. a Vermont union's
  // towns), plus entries for shapes whose own name differs (e.g. a Vermont town district).
  const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9 ]/g, " ").replace(/\bsaint\b/g, "st").replace(/\s+/g, " ");

  function buildSearch() {
    const groups = new Map();
    DRAW.forEach((n) => layers[n] && layers[n].eachLayer((l) => {
      const p = l.feature.properties;
      if (undefinedArea(l.feature) || isWorld(l.feature)) return;
      const r = rowFor(gid(l.feature));
      const id = (r && r["District ID"]) || (r && r.District) || gid(l.feature);
      const place = r ? (euOf(r["District ID"]) ? EU_NAMES[euOf(r["District ID"])] : [r.County, r.State || r.Territory || r.Province || r.Nation].filter(Boolean).join(", ")) : "";
      if (!groups.has(id)) groups.set(id, { name: r ? r.District : p.NAME, place, layers: [], scsd: n === "scsd" || n === "canada2", row: r });
      const g = groups.get(id);
      if ((n !== "scsd" && n !== "canada2") || g.scsd) g.layers.push(l);
      if (r && p.NAME && norm(p.NAME) !== norm(r.District) && n !== "scsd" && n !== "territories") {
        groups.set(`shape-${p.GEOID}`, { name: p.NAME, place, layers: [l], row: r, partOf: r.District });
      }
    }));
    byId = groups;
    searchIndex = [...groups.values()].filter((g) => g.layers.length).map((g) => ({
      ...g, text: norm(`${g.name} ${g.place}`), size: Number(String((g.row || {}).Enrollment || "").replace(/,/g, "")) || 0
    }));
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
    restyle: () => { if (map) restyle(); },
    // Zooms to and outlines a district by its District ID (used by the site-wide search).
    focus: (id) => loading && loading.then(() => { map.invalidateSize(); focusEntry(byId.get(id) || [...byId.values()].find((g) => g.row && g.row["District ID"] === id)); }),
    show(ds, datasets) {
      current = ds;
      if (!loading) {
        loading = Promise.all([...LAYERS, "aliases"].map((n) => fetch(`data/map/${n}.json`).then((r) => {
          if (!r.ok) {
            if (n === "world" || n === "canada" || n === "spm" || n === "uk" || n === "ireland" || Object.values(EU).includes(n)) return null;   // the US map still works without these borders
            throw new Error(`HTTP ${r.status}`);
          }
          return r.json();
        })))
          .then((files) => { aliases = files.pop(); build(datasets, files); $("map-status").textContent = ""; })
          .catch((e) => { $("map-status").textContent = `Couldn't load the map (${e.message}).`; throw e; });
      }
      loading.then(() => { map.invalidateSize(); restyle(); zoomToCurrent(); }).catch((e) => console.error("map:", e && e.stack));
    }
  };
})();
