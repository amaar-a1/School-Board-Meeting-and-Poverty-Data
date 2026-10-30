// "Map" tab: school district borders (Census 2024 cartographic boundaries, in docs/data/map/)
// colored by the site's data. app.js calls SiteMap.show() when the tab or the data set changes.
(function () {
  const $ = (id) => document.getElementById(id);
  const LAYERS = ["unsd", "elsd", "territories", "scsd"];   // drawing order; scsd only when ticked
  const JUMPS = {
    "Contiguous US": [[24.4, -125], [49.5, -66.9]],
    Alaska: [[51.2, -179.5], [71.5, -129.9]],
    Hawaii: [[18.8, -160.4], [22.3, -154.7]],
    "Puerto Rico": [[17.85, -67.3], [18.55, -65.2]],
    "U.S. Virgin Islands": [[17.65, -65.1], [18.45, -64.55]],
    Guam: [[13.2, 144.6], [13.7, 145.0]],
    "Northern Mariana Islands": [[14.0, 144.8], [15.4, 146.0]],
    "American Samoa": [[-14.6, -171.1], [-14.1, -168.1]]
  };
  const SCALES = {
    poverty: {
      column: "Percentage of Children Ages 5-17 in Poverty",
      breaks: [10, 15, 20, 25, 30],
      colors: ["#fef0d9", "#fdd49e", "#fdbb84", "#fc8d59", "#e34a33", "#b30000"],
      labels: ["Under 10%", "10–15%", "15–20%", "20–25%", "25–30%", "30% or more"]
    },
    meetings: {
      column: "Available Board Meetings",
      breaks: [1, 5, 15, 30],
      colors: ["#e7ecef", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
      labels: ["0", "1–4", "5–14", "15–29", "30 or more"]
    }
  };
  const NO_DATA = "#9e9e9e";

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
    let v = row ? toNumber(row[sc.column]) : NaN;
    if (metric === "meetings" && isNaN(v)) v = 0;   // no meetings found counts as 0
    if (isNaN(v)) return NO_DATA;
    const i = sc.breaks.findIndex((b) => v < b);
    return sc.colors[i === -1 ? sc.colors.length - 1 : i];
  }

  // In a state's view (or the territories'), districts elsewhere are faded.
  function inView(geoid) {
    if (!current || !current.state) return true;
    if (current.state === "territories") return /^(60|66|69|72|78)/.test(geoid);
    return !fips[current.state] || geoid.startsWith(fips[current.state]);
  }

  const undefinedArea = (f) => /^School District Not Defined$/i.test(f.properties.NAME || "");

  function style(feature) {
    if (undefinedArea(feature)) return { fillOpacity: 0, color: "#999", weight: 0.3, dashArray: "2 3" };
    const f = window.SiteFilters;
    let on = inView(feature.properties.GEOID);
    if (on && f && f.active()) {
      const r = rowFor(feature.properties.GEOID);
      on = !!r && f.test(r);
    }
    return { fillColor: color(rowFor(feature.properties.GEOID)), fillOpacity: on ? 0.8 : 0.15, color: "#555", weight: on ? 0.4 : 0.2 };
  }

  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function tip(feature) {
    const r = rowFor(feature.properties.GEOID);
    if (undefinedArea(feature)) return `<div class="map-tip"><strong>No school district</strong>Area the Census leaves outside any district (mostly water or federal land)</div>`;
    if (!r) return `<div class="map-tip"><strong>${esc(feature.properties.NAME)}</strong>Available board meetings: 0<br>No poverty data for this district</div>`;
    const place = [r.County, r.State || r.Territory].filter(Boolean).join(", ");
    const pov = toNumber(r["Percentage of Children Ages 5-17 in Poverty"]);
    const meet = toNumber(r["Available Board Meetings"]);
    const enr = toNumber(r.Enrollment);
    const note = [r["Map note"], r.Notes || r["Poverty figures"]].filter(Boolean).join(". ");
    return `<div class="map-tip"><strong>${esc(r.District)}${place ? `, ${esc(place)}` : ""}</strong>` +
      `Child poverty: ${isNaN(pov) ? "–" : pov.toFixed(1) + "%"}<br>` +
      `Available board meetings: ${isNaN(meet) ? "0 (no school board)" : meet.toLocaleString()}<br>` +
      `Enrollment: ${isNaN(enr) ? "not reported" : enr.toLocaleString()}` +
      (r.Locale ? `<br>Locale: ${esc(r.Locale)}` : "") +
      (note ? `<div class="tip-note">${esc(note)}</div>` : "") + "</div>";
  }

  function legend() {
    const sc = SCALES[$("map-metric").value];
    const items = sc.labels.map((l, i) => `<span><i style="background:${sc.colors[i]}"></i>${l}</span>`);
    if ($("map-metric").value !== "meetings") items.push(`<span><i style="background:${NO_DATA}"></i>No data</span>`);
    $("map-legend").innerHTML = items.join("");
  }

  function restyle() {
    Object.values(layers).forEach((l) => l.setStyle(style));
    legend();
  }

  function setSecondary() {
    const l = layers.scsd;
    if (!l) return;
    if ($("map-secondary").checked) l.addTo(map); else l.remove();
  }

  // Zooms to the selected state (or, for the territories, the first territory).
  function zoomToCurrent() {
    if (!map || !current) return;
    if (current.state === "territories") return jump("Puerto Rico");
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
    map = L.map("map", { preferCanvas: true, minZoom: 2, zoomSnap: 0.25 });
    L.tileLayer(`https://{s}.basemaps.cartocdn.com/${dark ? "dark_all" : "light_all"}/{z}/{x}/{y}{r}.png`, {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd", maxZoom: 14
    }).addTo(map);
    const renderer = L.canvas({ padding: 0.3 });
    LAYERS.forEach((name, i) => {
      const fc = topojson.feature(topo[i], topo[i].objects[name]);
      // Puerto Rico's border is in the unified-district file; the other territories use the territory outlines.
      if (name === "territories") fc.features = fc.features.filter((f) => f.properties.GEOID !== "7200030");
      else fc.features = fc.features.filter((f) => !/^(60|66|69|78)/.test(f.properties.GEOID));
      layers[name] = L.geoJSON(fc, {
        renderer, style,
        onEachFeature: (f, l) => {
          l.bindTooltip(() => tip(f), { sticky: true });
          l.on("click", () => map.fitBounds(l.getBounds(), { maxZoom: 11 }));
          l.on("mouseover", () => l.setStyle({ weight: 2, color: "#111" }));
          l.on("mouseout", () => l.setStyle(style(f)));
        }
      });
      if (name !== "scsd") layers[name].addTo(map);
    });
    const sel = $("map-jump");
    sel.add(new Option("—", ""));
    Object.keys(JUMPS).forEach((k) => sel.add(new Option(k, k)));
    sel.addEventListener("change", () => sel.value && jump(sel.value));
    $("map-metric").addEventListener("change", restyle);
    $("map-secondary").addEventListener("change", setSecondary);
    legend();
  }

  window.SiteMap = {
    rowFor: (geoid) => rowFor(geoid),
    restyle: () => { if (map) restyle(); },
    show(ds, datasets) {
      current = ds;
      if (!loading) {
        loading = Promise.all([...LAYERS, "aliases"].map((n) => fetch(`data/map/${n}.json`).then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })))
          .then((files) => { aliases = files.pop(); build(datasets, files); $("map-status").textContent = ""; })
          .catch((e) => { $("map-status").textContent = `Couldn't load the map (${e.message}).`; throw e; });
      }
      loading.then(() => { map.invalidateSize(); restyle(); zoomToCurrent(); }).catch(() => {});
    }
  };
})();
