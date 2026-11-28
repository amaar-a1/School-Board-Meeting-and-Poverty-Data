// "Compare" view: any two places on the site, from any countries, side by side. Each is picked by name (the same
// search as "Find a district"); the pair is kept in the link (?cmp=ID1,ID2) so a comparison can be shared.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const num = (v) => { const s = String(v ?? "").trim().replace(/[$,%\s]/g, ""); return s === "" ? NaN : Number(s); };
  const POV_COLS = ["Percentage of Children Ages 5-17 in Poverty", "Percentage of Children Ages 0-17 in Low Income", "Percentage of Children Under 16 in Low Income",
    "Percentage of Children in Low Income", "Poverty rate (all ages)", "Poverty rate or stand-in", "Poverty rate (region, all ages)",
    "Child low-income rate (estimated from its province)", "Unemployment rate (stand-in for poverty)"];
  const picked = [null, null];
  let byId = null;

  // Whole countries and their states, provinces or regions, as well as single places. An area's figures are made from
  // the places in it: totals for population, pupils and meetings, a population-weighted average for poverty, and its
  // lines over time linked year to year (history.js). Its ID in the link is "area:<country key>[:<region>]".
  let areas = null;
  const REGION_COLS = ["State", "Province", "Region", "Nation", "Department", "Territory"];
  function regionColOf(ds) {
    const cands = [ds.groups && ds.groups.column, ...REGION_COLS].filter(Boolean);
    for (const c of cands) { const v = new Set(ds.rows.map((r) => r[c]).filter(Boolean)); if (v.size >= 2 && v.size <= 150) return c; }
    return null;
  }
  let areasSig = "";
  function buildAreas() {
    const SD = window.SiteData, S = window.SiteSearch;
    // rebuilt when more countries' rows have loaded (and the search index with them)
    const sig = (SD ? SD.datasets : []).map((ds) => ds.rows.length).join(",") + (S ? "s" : "");
    if (areas && sig === areasSig) return areas;
    areasSig = sig;
    areas = [];
    (SD ? SD.datasets : []).forEach((ds) => {
      if (ds.combined || ds.country === "ISLE" || !ds.rows.length) return;
      const key = SD.keyOf(ds), cname = ds.button || (ds.groups && ds.groups.label) || ds.name;
      const add = (id, name, label, rows) => areas.push({ area: true, id, ds, label, rows, row: { District: name, "District ID": id },
        text: S ? S.norm(`${name} ${label}`) : name.toLowerCase(), size: 1e12 + rows.length });
      add(`area:${key}`, cname, `Country (${ds.rows.length.toLocaleString()} ${(ds.recordLabel || "places").toLowerCase()})`, ds.rows);
      const rc = regionColOf(ds);
      if (!rc) return;
      const names = rc === "State" && SD.config.perState ? SD.config.perState.names : {};
      [...new Set(ds.rows.map((r) => r[rc]).filter(Boolean))].forEach((g) => {
        const rows = ds.rows.filter((r) => r[rc] === g);
        add(`area:${key}:${g}`, String(names[g] || g).trim(), `${(ds.groups && ds.groups.word) || rc.toLowerCase()} of ${cname} (${rows.length.toLocaleString()} places)`, rows);
      });
    });
    return areas;
  }
  const entries = () => (window.SiteSearch ? window.SiteSearch.index : []);
  function entryById(id) {
    if (String(id).startsWith("area:")) return buildAreas().find((a) => a.id === String(id));
    if (!byId) { byId = new Map(); entries().forEach((e) => { if (e.row["District ID"] && !byId.has(e.row["District ID"])) byId.set(String(e.row["District ID"]), e); }); }
    return byId.get(String(id));
  }
  // An area's figures as one row with the site's usual columns, so it shows like a place.
  const AGG = new WeakMap();
  function aggregate(e) {
    if (AGG.has(e)) return AGG.get(e);
    const rows = e.rows, ds = e.ds, H = window.SiteHistory;
    const sum = (col, rs = rows) => rs.reduce((t, r) => t + (num(r[col]) > 0 ? num(r[col]) : 0), 0);
    const povCol = (r) => (ds.simple && ds.simple.pov && String(r[ds.simple.pov] ?? "").trim() !== "" && ds.simple.pov) || POV_COLS.find((c) => String(r[c] ?? "").trim() !== "");
    const weight = (r) => num(r.Population) > 0 ? num(r.Population) : num(r["Children Ages 5-17"]) > 0 ? num(r["Children Ages 5-17"]) : num(r.Children) > 0 ? num(r.Children) : 1;
    let pw = 0, pv = 0, pn = 0, pcol = "";
    rows.forEach((r) => { const c = povCol(r); const v = c ? num(r[c]) : NaN; if (!isNaN(v)) { pw += weight(r); pv += v * weight(r); pn++; pcol = pcol || c; } });
    const both = rows.filter((r) => num(r.Enrollment) > 0 && String(r["Public school enrollment"] ?? "") !== "" && !r["Enrollment estimated"]);
    const meet = rows.reduce((t, r) => t + (window.SiteData.meetOf(r, "Available Board Meetings") || 0), 0);
    const latest = rows.map((r) => r["Latest meeting"] || "").sort().pop() || "";
    const est = rows.some((r) => r["Enrollment estimated"]);
    const row = { District: e.row.District, "District ID": e.id, Population: sum("Population") || "", Enrollment: sum("Enrollment") || "",
      "Public school enrollment": both.length ? sum("Public school enrollment", both) : "", "Available Board Meetings": meet, "Latest meeting": latest,
      "Enrollment year": est ? `total of its places' figures; ${rows.filter((r) => r["Enrollment estimated"]).length.toLocaleString()} of them estimated (school-age children, no count published)` : "total of its places' figures", "School system": `${rows.length.toLocaleString()} ${(ds.recordLabel || "places").toLowerCase()}`,
      "Poverty measure": pn ? `average of ${pn.toLocaleString()} places' figures, weighted by population (${(povOf({ row: rows.find((r) => povCol(r)), ds }) || {}).measure || pcol})` : "" };
    if (pn) row[pcol] = (pv / pw).toFixed(2) + "%";
    // Density: its people over its land (each place's land from its population and density); locale: the one most of
    // its people live in. (For the map shown by region or country.)
    let dp = 0, da = 0;
    rows.forEach((r) => { const p = num(r.Population), d = num(r["People per km² (estimated)"]); if (p > 0 && d > 0) { dp += p; da += p / d; } });
    if (da > 0) row["People per km² (estimated)"] = Math.round(10 * dp / da) / 10;
    const loc = {};
    rows.forEach((r) => { if (r.Locale) loc[r.Locale] = (loc[r.Locale] || 0) + (num(r.Population) > 0 ? num(r.Population) : 1); });
    const lk = Object.keys(loc).sort((a, b) => loc[b] - loc[a])[0];
    if (lk) row.Locale = lk;
    row._pubBase = both.length ? sum("Enrollment", both) : 0;
    // Over time: each measure linked over the area's places; meetings added up.
    if (H) H.MEASURES.forEach((m) => {
      const series = rows.map((r) => (m.kind === "sum" ? H.parse(r[m.col]) : H.seriesOf(r, m.col))).filter((x) => Object.keys(x).length);
      let line = {};
      if (m.kind === "sum") series.forEach((x) => Object.entries(x).forEach(([y, v]) => { line[y] = (line[y] || 0) + v; }));
      else if (series.length) line = H.linked(series, m.kind);
      // the country's or region's own figures for years its places lack (data/area_history.json)
      if (m.kind !== "sum" && H.addArea) H.addArea(line, ds.name, e.id.split(":").slice(2).join(":"), m.col);
      const ys = Object.keys(line).sort();
      if (ys.length) row[m.col] = ys.map((y) => `${y}: ${line[y]}${m.unit === "%" ? "%" : ""}`).join("; ");
    });
    if (!H || !H.areaLoaded || H.areaLoaded()) AGG.set(e, row);   // not kept until the national and regional figures have loaded
    return row;
  }
  const rowOf = (e) => (e.area ? aggregate(e) : e.row);

  // One search box (slot 0 or 1): type, pick from the list with the mouse or the arrow keys and Enter.
  function wire(slot) {
    const box = $(`cmp-input-${slot}`), list = $(`cmp-results-${slot}`);
    let shown = [], active = -1;
    const hide = () => { list.hidden = true; box.setAttribute("aria-expanded", "false"); };
    box.addEventListener("input", () => {
      const S = window.SiteSearch;
      const q = S ? S.norm(box.value).trim() : "";
      active = -1;
      if (q.length < 2) return hide();
      const words = q.split(/\s+/);
      shown = buildAreas().concat(entries()).filter((e) => words.every((w) => e.text.includes(w)))
        .sort((a, b) => (S.norm(b.row.District).startsWith(q) - S.norm(a.row.District).startsWith(q)) || b.size - a.size).slice(0, 8);
      list.innerHTML = shown.length
        ? shown.map((e, i) => `<li role="option" data-i="${i}" aria-selected="false"><strong>${esc(e.row.District)}</strong><span>${esc(e.label)}</span></li>`).join("")
        : `<li class="map-results-none">No place found</li>`;
      list.hidden = false;
      box.setAttribute("aria-expanded", "true");
    });
    box.addEventListener("keydown", (e) => {
      const items = [...list.querySelectorAll("li[data-i]")];
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!items.length) return;
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((li, i) => li.setAttribute("aria-selected", String(i === active)));
      } else if (e.key === "Enter") {
        e.preventDefault();
        const li = items[active >= 0 ? active : 0];
        if (li) { set(slot, shown[Number(li.dataset.i)]); hide(); }
      } else if (e.key === "Escape") hide();
    });
    list.addEventListener("mousedown", (e) => {
      const li = e.target.closest("li[data-i]");
      if (li) { e.preventDefault(); set(slot, shown[Number(li.dataset.i)]); hide(); }
    });
    box.addEventListener("blur", () => setTimeout(hide, 150));
  }

  function set(slot, entry, quiet) {
    picked[slot] = entry || null;
    $(`cmp-input-${slot}`).value = entry ? entry.row.District : "";
    if (!quiet && window.SiteLinks) window.SiteLinks.set({ cmp: picked.map((e) => (e ? e.row["District ID"] : "")).join(",").replace(/^,$/, "") });
    render();
  }

  function povOf(e) {
    const r = e.area ? rowOf(e) : e.row, ds = e.ds;
    const col = (ds.simple && ds.simple.pov && String(r[ds.simple.pov] ?? "").trim() !== "" && ds.simple.pov) || POV_COLS.find((c) => String(r[c] ?? "").trim() !== "");
    const q = window.SiteQuality ? window.SiteQuality.quality(ds) : null;
    return { v: col ? num(r[col]) : NaN, measure: r["Poverty measure"] || (q && q.measure) || col || "", est: !e.area && (!!r._rankEst || /estimat/i.test(col || "")) };
  }

  // The figures shown for each place: [label, value, note].
  function fields(e) {
    const r = rowOf(e), ds = e.ds, p = povOf(e);
    const enr = num(r.Enrollment), pub = num(r["Public school enrollment"]), pop = num(r.Population), dens = num(r["People per km² (estimated)"]);
    const pubBase = e.area ? r._pubBase : enr;
    const meet = window.SiteData.meetOf(r, "Available Board Meetings");
    const estEnr = !e.area && (r["Enrollment estimated"] || /estimated/i.test(r["Enrollment year"] || ""));
    const where = e.area ? (e.id.split(":").length > 2 ? (ds.button || (ds.groups && ds.groups.label) || ds.name) : "Whole country") : ds.country && ds.country !== "US" ? (ds.country === "ISLE" ? r.District : ds.name) : "United States";
    return [
      ["Country", where, e.label],
      ["Poverty", isNaN(p.v) ? "–" : `${p.v.toFixed(1)}%`, p.measure + (p.est ? " (estimated from a wider area)" : "")],
      ["Poverty rank in its country", String(r["Poverty rank in country"] ?? "") !== "" ? `${r["Poverty rank in country"]} of 100` : "–", e.area ? "" : "100 = the highest poverty in its country" + (r._rankEst ? "; estimated" : "")],
      ["Meetings found", isNaN(meet) ? "0" : meet.toLocaleString(), [r["Meeting body"], r["Meetings type"]].filter(Boolean).join(": ")],
      ["Latest meeting", r["Latest meeting"] || "–", ""],
      ["Enrollment", isNaN(enr) ? "–" : enr.toLocaleString(), estEnr ? "estimated: school-age children, no count published" : r["Enrollment year"] || ""],
      ["Public schools' share", pub > 0 && pubBase > 0 && (e.area || !estEnr) ? `${Math.round(100 * pub / pubBase)}%` : "–", e.area && pub > 0 ? "of the pupils in its places that report both counts" : ""],
      ["Population", isNaN(pop) ? "–" : pop.toLocaleString(), ""],
      ["People per km²", isNaN(dens) ? "–" : dens.toLocaleString(), r.Locale ? `locale: ${r.Locale}` : ""],
      ["School system", r["School system"] || r["Board type"] || "–", ""]
    ];
  }

  function qualityCell(e) {
    const Q = window.SiteQuality;
    if (!Q) return "";
    const holder = document.createElement("p");
    holder.className = "quality";
    Q.renderFor(e.ds, holder);
    holder.hidden = false;
    return holder.outerHTML;
  }

  function render() {
    const out = $("cmp-body");
    if (!out) return;
    const [a, b] = picked;
    $("cmp-download").disabled = !(a && b);
    const hist = $("cmp-history");
    if (hist && window.SiteHistory) window.SiteHistory.renderPlaces(hist, [a, b].map((e) => e && { name: e.row.District, row: rowOf(e) }), { title: "Over time" });
    if (!a && !b) { out.innerHTML = `<p class="muted">Pick two places to compare them.</p>`; return; }
    const fa = a ? fields(a) : null, fb = b ? fields(b) : null;
    const rows = (fa || fb).map((f, i) => [f[0], fa && fa[i], fb && fb[i]]);
    const cell = (f) => (f ? `<div class="cmp-v">${esc(f[1])}</div>${f[2] ? `<div class="cmp-sub">${esc(f[2])}</div>` : ""}` : `<span class="muted">Pick a place</span>`);
    out.innerHTML = `<div class="table-wrap"><table class="data-table cmp-table"><thead><tr><th></th><th>${a ? esc(a.row.District) : "–"}</th><th>${b ? esc(b.row.District) : "–"}</th></tr></thead><tbody>` +
      rows.map(([l, x, y]) => `<tr><th scope="row">${esc(l)}</th><td>${cell(x)}</td><td>${cell(y)}</td></tr>`).join("") +
      `<tr><th scope="row">Data quality (its country)</th><td>${a ? qualityCell(a) : ""}</td><td>${b ? qualityCell(b) : ""}</td></tr>` +
      `</tbody></table></div>` +
      (a && a.area || b && b.area ? `<p class="note">A country's or region's figures are made from its places on this site: totals for population, pupils and meetings, and an average of its places' poverty figures weighted by their population, so they can differ from the official figure for the whole area.</p>` : "") +
      (a && b && a.ds !== b.ds ? `<p class="note">These places are in different countries, which measure poverty in different ways and count different bodies' meetings, so compare their ranks within their countries rather than their poverty figures.</p>` : "");
  }

  function download() {
    const [a, b] = picked;
    if (!(a && b)) return;
    const fa = fields(a), fb = fields(b);
    const csv = window.Papa.unparse({ fields: ["Field", a.row.District, `${a.row.District} (note)`, b.row.District, `${b.row.District} (note)`],
      data: fa.map((f, i) => [f[0], f[1], f[2], fb[i][1], fb[i][2]]) });
    const el = document.createElement("a");
    el.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    el.download = `compare-${[a, b].map((e) => String(e.row.District).replace(/\W+/g, "-").toLowerCase()).join("-vs-")}.csv`;
    el.click();
    URL.revokeObjectURL(el.href);
  }

  // From the link (?cmp=ID1,ID2) or from "Compare with another place" on a Find card.
  function load(ids) {
    const go = () => { (ids || []).slice(0, 2).forEach((id, i) => { if (id) set(i, entryById(id), true); }); render(); };
    if (window.SiteSearch) go(); else document.addEventListener("site-search-ready", go, { once: true });
  }
  function start(id) {
    window.SiteData.setView("compare");
    history.replaceState(null, "", "#compare");
    set(0, entryById(id));
    $("cmp-input-1").focus();
    $("compare-view").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  [0, 1].forEach(wire);
  $("cmp-swap").addEventListener("click", () => { const [a, b] = picked; set(0, b, true); set(1, a); });
  $("cmp-download").addEventListener("click", download);
  const q = new URLSearchParams(location.search).get("cmp");
  if (q) load(q.split(","));
  else render();
  // For the Trends tab's "Add places": the same search over places, regions and countries, and an entry's row.
  function find(text, n = 8) {
    const S = window.SiteSearch;
    const q = S ? S.norm(text).trim() : String(text).toLowerCase().trim();
    if (q.length < 2) return [];
    const words = q.split(/\s+/);
    return buildAreas().concat(entries()).filter((e) => words.every((w) => e.text.includes(w)))
      .sort((a, b) => (S.norm(b.row.District).startsWith(q) - S.norm(a.row.District).startsWith(q)) || b.size - a.size).slice(0, n);
  }
  window.SiteCompare = { start, load, render, find, rowOf, entryById, areas: buildAreas, picked: () => picked.map((e) => e && e.row["District ID"]) };
})();
