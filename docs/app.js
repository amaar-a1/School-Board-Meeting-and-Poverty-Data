(function () {
  const cfg = window.SITE_CONFIG;
  const $ = (id) => document.getElementById(id);
  let datasets = [];   // [{ name, columns, rows, numeric: Set }]
  let combined = null; // the "All" view: every data set's rows in shared columns (see cfg.combined)
  let current = null;
  let sort = { col: null, dir: 1 };
  let chart = null;
  const subsetCharts = {};
  const TABLE_LIMIT = 500;   // rows drawn at once; the full set is still searchable and downloadable
  const sizeCharts = {};
  let view = "overview";
  // A data set can bring its own comparison columns (Canada uses low income for ages 0-17).
  const cmpFor = (d) => (d && d.compare) || cfg.compare;

  document.title = cfg.title;
  $("site-title").textContent = cfg.title;
  $("sources-link").href = cfg.sourcesUrl;

  async function fetchCsv(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    if (text.trim().startsWith("<")) throw new Error("not a CSV file");
    return text;
  }

  function toNumber(v) {
    if (v == null) return NaN;
    const s = String(v).trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  }

  function parse(name, text, opts = {}) {
    const out = Papa.parse(text, { header: true, skipEmptyLines: "greedy" });
    const filled = (v) => String(v ?? "").trim() !== "";
    let columns = (out.meta.fields || []).filter((c) => c && c.trim() !== "");
    const rows = out.data.filter((r) => columns.some((c) => filled(r[c])));
    columns = columns.filter((c) => rows.some((r) => filled(r[c])));
    const textCols = new Set(opts.textColumns || []);
    const numeric = new Set(columns.filter((c) => {
      if (textCols.has(c)) return false;
      const vals = rows.map((r) => r[c]).filter(filled);
      return vals.length > 0 && vals.every((v) => !isNaN(toNumber(v)));
    }));
    const percent = new Set([...numeric].filter((c) =>
      rows.map((r) => r[c]).filter(filled).every((v) => String(v).trim().endsWith("%"))));
    return { ...opts, name, columns, rows, numeric, percent };
  }

  async function load() {
    try {
      datasets = await Promise.all(cfg.dataFiles.map(async (d) => parse(d.name, await fetchCsv(d.file), d)));
      datasets.forEach((d) => {
        if (!d.note) return;
        const withMeetings = d.rows.filter((r) => toNumber(r[cmpFor(d).by]) > 0).length;
        d.note = d.note.replace("{rows}", d.rows.length.toLocaleString()).replace("{withMeetings}", withMeetings.toLocaleString());
      });
      if (cfg.combined) combined = buildCombined(cfg.combined);
      $("status").textContent = "";
    } catch (err) {
      $("status").classList.add("error");
      $("status").textContent = `Couldn't load the data (${err.message}). Please try again later.`;
      return;
    }
    renderTabs();
    setupFilters();
    window.SiteData = { datasets, combined, config: cfg, setView, select: (key) => selectDataset(key ? stateDataset(key) : datasets.find((d) => d.name === cfg.perState.from)) };
    selectDataset(datasets.find((d) => d.name === (cfg.perState && cfg.perState.from)) || datasets[0]);
  }

  // The "All" view: US districts, territory school systems and Canadian boards in one table, with
  // shared columns. Their poverty measures differ, so each row says which one it uses.
  function buildCombined(c) {
    const ps = cfg.perState, out = [];
    const pct = (v) => (String(v ?? "").trim() === "" ? "" : `${toNumber(v).toFixed(2)}%`);
    datasets.forEach((d) => d.rows.forEach((r) => {
      const ca = d.country === "CA", terr = !!d.state;
      out.push({
        District: r.District,
        Country: ca ? "Canada" : terr ? "U.S. territories" : "United States",
        "State or province": ca ? r.Province : terr ? r.Territory : (ps.names[r.State] || r.State),
        "Available Board Meetings": r["Available Board Meetings"] ?? "",
        [c.metric]: pct(ca ? r["Percentage of Children Ages 0-17 in Low Income"] : r["Percentage of Children Ages 5-17 in Poverty"]),
        "Poverty measure": ca ? c.measures.canada : terr ? c.measures.territories : c.measures.us,
        Children: ca ? r["Children Ages 0-17"] : r["Children Ages 5-17"],
        Enrollment: r.Enrollment ?? "",
        Locale: r.Locale ?? "",
        "Other Board Meetings": r["Other Board Meetings"] ?? "",   // DC, Hawaiʻi and Vermont boards' own sites
        "District ID": r["District ID"]
      });
    }));
    const text = Papa.unparse({ fields: Object.keys(out[0]), data: out.map((r) => Object.values(r)) });
    const ds = parse(c.name, text, { ...c, combined: true });
    const withMeetings = ds.rows.filter((r) => toNumber(r[c.compare.by]) > 0).length;
    ds.note = (c.note || "").replace("{rows}", ds.rows.length.toLocaleString()).replace("{withMeetings}", withMeetings.toLocaleString());
    return ds;
  }

  // One state's view: its own data set if there is one (the territories), otherwise
  // the national rows for that state.
  const stateCache = {};
  function stateDataset(abbr) {
    const ps = cfg.perState;
    if (!ps) return null;
    if (stateCache[abbr]) return stateCache[abbr];
    const own = datasets.find((d) => d.state === abbr);
    if (own) return (stateCache[abbr] = own);
    // "CA:ON" and the like: one province or territory of another country's data set.
    const [country, code] = abbr.includes(":") ? abbr.split(":") : [null, abbr];
    const parent = country ? datasets.find((d) => d.country === country) : null;
    const nat = parent || datasets.find((d) => d.name === ps.from);
    if (!nat) return null;
    const groupCol = parent ? parent.groups.column : ps.column;
    const name = parent ? parent.groups.names[code] : ps.names[abbr];
    // The other country's file names its provinces in full ("Ontario"); the menu keys are codes.
    const rows = nat.rows.filter((r) => r[groupCol] === (parent ? name : code));
    const withMeetings = rows.filter((r) => toNumber(r[cmpFor(nat).by]) > 0).length;
    const label = (nat.recordLabel || cfg.recordLabel || "records").toLowerCase();
    if (parent && parent.groupNotes && parent.groupNotes[code]) {
      return (stateCache[abbr] = { ...nat, name, state: abbr, rows, sourcesAs: nat.name, parent: nat,
        columns: nat.columns.filter((c) => c !== groupCol), note: parent.groupNotes[code] });
    }
    return (stateCache[abbr] = { ...nat, name, state: abbr, rows, sourcesAs: nat.name, parent: parent || undefined,
      columns: nat.columns.filter((c) => c !== groupCol),
      note: rows.length === 1
        ? `1 school ${label.replace(/s$/, "")} in ${name}. ${withMeetings ? "Its meeting count is available." : "No meeting count is available, so it shows 0."}`
        : `${rows.length.toLocaleString()} school ${label} in ${name}. Meeting counts are available for ${withMeetings.toLocaleString()} of them; the rest show 0.` });
  }

  // "Data:" row: a button for the national data and a menu with every state.
  function renderTabs() {
    const tabs = $("tabs"), ps = cfg.perState;
    tabs.hidden = false;
    tabs.innerHTML = '<span class="tabs-label">Data:</span>';
    // One button per country-wide data set: the US (perState.from) and any with a `country`.
    const buttons = datasets.filter((d) => (ps && d.name === ps.from) || d.country);
    buttons.forEach((d, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.role = "tab";
      b.className = "country-button";
      if (i === 0) b.id = "national-button";
      b.dataset.name = d.name;
      b.textContent = d.name;
      b.addEventListener("click", () => selectDataset(d));
      tabs.appendChild(b);
    });
    if (combined) {
      const b = document.createElement("button");
      b.type = "button";
      b.role = "tab";
      b.className = "country-button";
      b.dataset.name = combined.name;
      b.textContent = combined.button || combined.name;
      b.title = combined.name;
      b.addEventListener("click", () => selectDataset(combined));
      tabs.appendChild(b);
    }
    const sel = document.createElement("select");
    sel.id = "state-select";
    sel.setAttribute("aria-label", "State or province");
    const others = datasets.filter((d) => d.country && d.groups);
    sel.add(new Option(others.length ? "Choose a state or province…" : "Choose a state…", ""));
    const group = (label) => {
      if (!others.length) return sel;
      const g = document.createElement("optgroup");
      g.label = label;
      sel.appendChild(g);
      return g;
    };
    const us = group("United States");
    Object.entries(ps ? ps.names : {}).sort((a, b) => a[1].localeCompare(b[1]))
      .forEach(([abbr, name]) => us.appendChild(new Option(name, abbr)));
    Object.entries((ps && ps.after) || {}).forEach(([key, name]) => us.appendChild(new Option(name, key)));
    others.forEach((d) => {
      const g = group(d.groups.label || d.name);
      Object.entries(d.groups.names).sort((a, b) => a[1].localeCompare(b[1]))
        .filter(([, name]) => d.rows.some((r) => r[d.groups.column] === name))
        .forEach(([code, name]) => g.appendChild(new Option(name, `${d.country}:${code}`)));
    });
    sel.addEventListener("change", () => { if (sel.value) selectDataset(stateDataset(sel.value)); });
    tabs.appendChild(sel);
  }

  function selectDataset(ds) {
    current = ds;
    sort = { col: null, dir: 1 };
    const sel = $("state-select");
    document.querySelectorAll(".country-button").forEach((b) => b.setAttribute("aria-selected", String(!current.state && b.dataset.name === current.name)));
    if (sel) { sel.value = current.state || ""; sel.classList.toggle("active", !!current.state); }
    $("dataset-note").textContent = current.note || "";
    $("footer").textContent = current.footer || "";
    renderSources();
    renderRules();
    $("search").value = "";
    renderStats();
    setupChartControls();
    applyFilters();
    $("table-section").hidden = false;
    $("filters").hidden = !["overview", "map"].includes(view);
    // Locale and size filters need NCES columns, which Canada's data doesn't have.
    const locSel = $("f-locale"), keepLoc = locSel.value;
    locSel.innerHTML = '<option value="">Any</option>';
    localeGroups(current.rows).forEach((g) => locSel.add(new Option(g, g)));
    locSel.value = [...locSel.options].some((o) => o.value === keepLoc) ? keepLoc : "";
    ["f-locale", "f-size"].forEach((id) => {
      const has = id === "f-locale" ? current.columns.includes("Locale") : current.columns.includes(cfg.sizeTiers.column);
      $(id).closest("label").hidden = !has;
      if (!has) $(id).value = "";
    });
    if (view === "size") renderSize();
    if (view === "locale") renderLocale();
    if (view === "map" && window.SiteMap) window.SiteMap.show(current, datasets);
  }

  // Switches between the "Overview", "By district size", "State rules" and "Sources" views.
  function setView(name) {
    view = name;
    document.querySelectorAll("[data-view]").forEach((el) => { el.hidden = el.dataset.view !== name; });
    document.querySelectorAll("[data-view-tab]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.viewTab === name)));
    $("filters").hidden = !current || !["overview", "map"].includes(name);
    if (name === "size" && current) renderSize();
    if (name === "locale" && current) renderLocale();
    if (name === "map" && current && window.SiteMap) window.SiteMap.show(current, datasets);
  }

  const avg = (vals) => (vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : NaN);
  const pct = (n) => (isNaN(n) ? "–" : `${n.toFixed(1)}%`);
  const fixed = (n, digits) => (isNaN(n) ? "–" : n.toFixed(digits));

  // Stats for one group of rows, used by the "By district size" tab.
  function sizeStats(rows, enrollCol) {
    const cmp = cmpFor(current);
    const meetings = (r) => toNumber(r[cmp.by]);
    const poverty = (r) => toNumber(r[cmp.metric]);
    const withM = rows.filter((r) => meetings(r) > 0), withoutM = rows.filter((r) => meetings(r) === 0);
    const totalMeetings = rows.reduce((a, r) => a + (meetings(r) || 0), 0);
    const totalEnroll = rows.reduce((a, r) => a + (toNumber(r[enrollCol]) || 0), 0);
    const avgMeetings = rows.length ? totalMeetings / rows.length : NaN;
    const avgPoverty = avg(rows.map(poverty).filter((v) => !isNaN(v)));
    return {
      n: rows.length, nWith: withM.length, nWithout: withoutM.length,
      shareWith: rows.length ? (100 * withM.length) / rows.length : NaN,
      avgMeetings,
      povWith: avg(withM.map(poverty).filter((v) => !isNaN(v))),
      povWithout: avg(withoutM.map(poverty).filter((v) => !isNaN(v))),
      per10k: totalEnroll ? (totalMeetings / totalEnroll) * 10000 : NaN,
      perPovPoint: avgPoverty ? avgMeetings / avgPoverty : NaN
    };
  }

  // "By locale" tab: the same comparisons as "By district size", grouped by locale. US districts
  // use NCES locale types; Canadian boards an estimate from Statistics Canada population sizes.
  const LOCALE_ORDER = ["Urban", "Suburban", "Town", "Rural", "Large urban", "Medium urban", "Small urban", "Province-wide"];
  function localeGroups(rows) {
    const seen = new Set(rows.map((r) => String(r.Locale || "").trim()).filter(Boolean));
    const order = LOCALE_ORDER.filter((g) => seen.has(g));
    return [...order, ...[...seen].filter((g) => !order.includes(g)).sort()];
  }

  function renderLocale() {
    const has = current.columns.includes("Locale");
    const ok = has && canCompare();
    $("locale-missing").textContent = has ? `This tab needs meeting counts and child poverty figures, which aren't available for ${current.name}.`
      : "This tab needs a “Locale” column in the data.";
    $("locale-missing").hidden = ok;
    $("locale-content").hidden = !ok;
    if (!ok) return;
    const label = ((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase();
    // Meetings per 10,000 students, or per 10,000 children where there's no enrollment (Canada).
    const denom = current.columns.includes("Enrollment") && current.rows.some((r) => toNumber(r.Enrollment) > 0) ? "Enrollment"
      : ["Children Ages 0-17", "Children", "Children Ages 5-17"].find((c) => current.columns.includes(c));
    const per = denom === "Enrollment" ? "students" : "children";
    const names = localeGroups(current.rows);
    const groups = names.map((g) => ({ name: g, s: sizeStats(current.rows.filter((r) => String(r.Locale || "").trim() === g), denom) }));
    const all = sizeStats(current.rows.filter((r) => String(r.Locale || "").trim()), denom);
    const left = current.rows.filter((r) => !String(r.Locale || "").trim()).length;
    const ca = current.country === "CA" || (current.parent && current.parent.country === "CA");
    $("locale-note").textContent = (ca ? "Boards are grouped by an estimated locale (see below)." : current.combined
      ? "US districts are grouped by NCES locale (2023); Canadian boards by an estimated locale (see below)."
      : "Districts are grouped by NCES locale (2023): Urban (a city), Suburban, Town or Rural.") +
      (left ? ` ${left.toLocaleString()} ${label} without a locale are left out of this tab.` : "");
    $("locale-def").textContent = ca || current.combined
      ? "Canada's locales are estimates, after Statistics Canada's population centre sizes: each census subdivision (municipality) with 100,000+ people is large urban; one with at least 150 people per km² (the OECD's rural cutoff) is medium urban (30,000–99,999 people) or small urban (1,000–29,999); the rest are rural. A board takes the locale where most of its children live; boards serving a whole province or territory are “Province-wide”. They aren't the same as the US NCES locales."
      : "";
    const cols = ["Locale", label[0].toUpperCase() + label.slice(1), "With meetings", "Avg meetings", "Poverty: with meetings", "Poverty: without",
      `Meetings per 10,000 ${per}`, "Meetings per poverty point"];
    const cells = (name, s) => s.n ? [name, s.n.toLocaleString(), `${pct(s.shareWith)} (${s.nWith})`, fixed(s.avgMeetings, 2),
      s.nWith ? `${pct(s.povWith)} (${s.nWith})` : "–", s.nWithout ? `${pct(s.povWithout)} (${s.nWithout})` : "–",
      fixed(s.per10k, 2), fixed(s.perPovPoint, 3)] : [name, "0", "–", "–", "–", "–", "–", "–"];
    const table = $("locale-table");
    table.tHead.innerHTML = "";
    const hr = table.tHead.insertRow();
    cols.forEach((c, i) => { const th = document.createElement("th"); th.textContent = c; if (i) th.className = "num"; hr.appendChild(th); });
    const body = table.tBodies[0];
    body.innerHTML = "";
    [...groups.map((g) => cells(g.name, g.s)), cells(`All ${label}`, all)].forEach((vals, i) => {
      const tr = body.insertRow();
      if (i === groups.length) tr.className = "total";
      vals.forEach((v, j) => { const td = tr.insertCell(); td.textContent = v; if (j) td.className = "num"; });
    });
    const accent = cssVar("--accent"), accent2 = cssVar("--accent-2"), text = cssVar("--muted"), grid = cssVar("--border");
    const labels = groups.map((g) => g.name);
    const axes = (yTitle) => ({ x: { ticks: { color: text }, grid: { display: false } },
      y: { beginAtZero: true, title: { display: true, text: yTitle, color: text }, ticks: { color: text }, grid: { color: grid } } });
    const legend = { labels: { color: text } };
    const draw = (id, config) => { if (sizeCharts[id]) sizeCharts[id].destroy(); sizeCharts[id] = new Chart($(id), config); };
    const tip = (i) => `${i.dataset.label}: ${pct(i.raw)} (${i.dataset.counts[i.dataIndex]} ${label})`;
    draw("locale-poverty-chart", { type: "bar",
      data: { labels, datasets: [
        { label: "With available meetings", data: groups.map((g) => (g.s.nWith ? g.s.povWith : null)), counts: groups.map((g) => g.s.nWith), backgroundColor: accent, borderRadius: 3 },
        { label: "Without", data: groups.map((g) => (g.s.nWithout ? g.s.povWithout : null)), counts: groups.map((g) => g.s.nWithout), backgroundColor: accent2, borderRadius: 3 }] },
      options: { maintainAspectRatio: false, scales: axes("Average child poverty rate (%)"), plugins: { legend, tooltip: { callbacks: { label: tip } } } } });
    draw("locale-share-chart", { type: "bar",
      data: { labels, datasets: [
        { label: "With available meetings", data: groups.map((g) => g.s.shareWith), counts: groups.map((g) => g.s.nWith), backgroundColor: accent },
        { label: "Without", data: groups.map((g) => 100 - g.s.shareWith), counts: groups.map((g) => g.s.nWithout), backgroundColor: accent2 }] },
      options: { maintainAspectRatio: false,
        scales: { x: { stacked: true, ticks: { color: text }, grid: { display: false } },
                  y: { stacked: true, max: 100, title: { display: true, text: `Share of ${label} (%)`, color: text }, ticks: { color: text }, grid: { color: grid } } },
        plugins: { legend, tooltip: { callbacks: { label: tip } } } } });
    draw("locale-meetings-chart", { type: "bar",
      data: { labels, datasets: [{ label: "Average available meetings", data: groups.map((g) => g.s.avgMeetings), counts: groups.map((g) => g.s.n), backgroundColor: accent, borderRadius: 3 }] },
      options: { maintainAspectRatio: false, scales: axes("Average available meetings"),
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (i) => `${i.raw.toFixed(2)} meetings on average (${i.dataset.counts[i.dataIndex]} ${label})` } } } } });
  }

  function statCard(parent, label, value, sub) {
    const d = document.createElement("div");
    d.className = "stat";
    d.innerHTML = '<div class="label"></div><div class="value"></div><div class="sub"></div>';
    d.querySelector(".label").textContent = label;
    d.querySelector(".value").textContent = value;
    d.querySelector(".sub").textContent = sub || "";
    parent.appendChild(d);
  }

  function renderSize() {
    const st = cfg.sizeTiers;
    const enrollCol = st && current.columns.find((c) => c.trim().toLowerCase() === st.column.toLowerCase());
    const ok = enrollCol && canCompare();
    const missing = [[cmpFor(current).by, "meeting counts"], [cmpFor(current).metric, "child poverty figures"]]
      .filter(([c]) => !current.numeric.has(c)).map(([, label]) => label).join(" and ");
    $("size-missing").textContent = enrollCol
      ? `This tab needs ${missing}, which aren't available for ${current.name}.`
      : current.sizeNote || "This tab needs an “Enrollment” column in the data.";
    $("size-missing").hidden = ok;
    $("size-content").hidden = !ok;
    if (!ok) return;
    const enroll = (r) => toNumber(r[enrollCol]);
    const rows = current.rows.filter((r) => !isNaN(enroll(r)));
    const range = (t) => (t.max == null ? `${t.min.toLocaleString()}+` : `${t.min.toLocaleString()}–${t.max.toLocaleString()}`);
    const tiers = st.tiers.map((t) => ({ ...t,
      s: sizeStats(rows.filter((r) => enroll(r) >= t.min && (t.max == null || enroll(r) <= t.max)), enrollCol) }));
    const all = sizeStats(rows, enrollCol);
    const label = ((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase();
    const left = current.rows.length - rows.length;
    $("size-note").textContent = "Districts are grouped by student enrollment (2023)." +
      (left ? ` ${left.toLocaleString()} ${label} without an enrollment figure are left out of this tab.` : "");

    // This state's rules on recording or streaming meetings (state views only)
    const sr = window.STATE_RULES;
    $("size-law").hidden = !current.state || !sr;
    if (current.state && sr) {
      const rules = sr.laws.filter((x) => x.state === current.name);
      $("law-title").textContent = `${current.name} rules on recording or streaming board meetings`;
      const list = $("law-list");
      list.innerHTML = "";
      (rules.length ? rules : [null]).forEach((x) => {
        const li = document.createElement("li");
        if (x) {
          const b = document.createElement("strong");
          b.textContent = `${x.covers}: `;
          li.append(b, x.rule);
        } else {
          li.textContent = current.rulesNote ||
            `No recording or streaming requirement found (checked ${sr.checked}); usually only written minutes are required.`;
        }
        list.appendChild(li);
      });
      const lawBody = $("law-body");
      lawBody.innerHTML = "";
      $("law-note").textContent = rules.filter((x) => x.enrollmentMin && x.enrollmentNote).map((x) => x.enrollmentNote).join(" ");
      rules.filter((x) => x.enrollmentMin).forEach((x) => {
        const covered = sizeStats(rows.filter((r) => enroll(r) >= x.enrollmentMin), enrollCol);
        statCard(lawBody, `Districts with ${x.enrollmentMin.toLocaleString()}+ students`, covered.n.toLocaleString(), x.requiredLabel);
        statCard(lawBody, "Of those, with available meetings", pct(covered.shareWith), `${covered.nWith.toLocaleString()} of ${covered.n.toLocaleString()} ${label}`);
        statCard(lawBody, "Of those, with none found", pct(100 - covered.shareWith), `${covered.nWithout.toLocaleString()} ${label}`);
      });
    }

    // Overall
    const overall = $("size-overall");
    overall.innerHTML = "";
    statCard(overall, "Districts with available meetings", pct(all.shareWith), `${all.nWith.toLocaleString()} of ${all.n.toLocaleString()} ${label}`);
    statCard(overall, "Average available meetings", fixed(all.avgMeetings, 2), "per district");
    statCard(overall, "Meetings per 10,000 students", fixed(all.per10k, 2), "meeting-to-population ratio");
    statCard(overall, "Meetings per poverty point", fixed(all.perPovPoint, 3), "meeting-to-poverty-rate ratio");

    // Table
    const cols = ["Tier", "Enrollment", "Districts", "With meetings", "Avg meetings",
      "Poverty: with meetings", "Poverty: without", "Meetings per 10,000 students", "Meetings per poverty point"];
    const cells = (name, rng, s) => s.n ? [name, rng, s.n.toLocaleString(), `${pct(s.shareWith)} (${s.nWith})`, fixed(s.avgMeetings, 2),
      s.nWith ? `${pct(s.povWith)} (${s.nWith})` : "–", s.nWithout ? `${pct(s.povWithout)} (${s.nWithout})` : "–",
      fixed(s.per10k, 2), fixed(s.perPovPoint, 3)] : [name, rng, "0", "–", "–", "–", "–", "–", "–"];
    const table = $("size-table");
    table.tHead.innerHTML = "";
    const hr = table.tHead.insertRow();
    cols.forEach((c, i) => { const th = document.createElement("th"); th.textContent = c; if (i > 1) th.className = "num"; hr.appendChild(th); });
    const body = table.tBodies[0];
    body.innerHTML = "";
    [...tiers.map((t) => cells(t.name, range(t), t.s)), cells("All districts", "", all)].forEach((vals, i) => {
      const tr = body.insertRow();
      if (i === tiers.length) tr.className = "total";
      vals.forEach((v, j) => { const td = tr.insertCell(); td.textContent = v; if (j > 1) td.className = "num"; });
    });

    // Charts
    const accent = cssVar("--accent"), accent2 = cssVar("--accent-2"), text = cssVar("--muted"), grid = cssVar("--border");
    const labels = tiers.map((t) => `${t.name} (${range(t)})`);
    const axes = (yTitle, extra) => ({
      x: { ticks: { color: text }, grid: { display: false }, ...(extra || {}) },
      y: { beginAtZero: true, title: { display: true, text: yTitle, color: text }, ticks: { color: text }, grid: { color: grid }, ...(extra || {}) }
    });
    const legend = { labels: { color: text } };
    const draw = (id, config) => { if (sizeCharts[id]) sizeCharts[id].destroy(); sizeCharts[id] = new Chart($(id), config); };

    draw("size-poverty-chart", {
      type: "bar",
      data: { labels, datasets: [
        { label: "With available meetings", data: tiers.map((t) => (t.s.nWith ? t.s.povWith : null)), counts: tiers.map((t) => t.s.nWith), backgroundColor: accent, borderRadius: 3 },
        { label: "Without", data: tiers.map((t) => (t.s.nWithout ? t.s.povWithout : null)), counts: tiers.map((t) => t.s.nWithout), backgroundColor: accent2, borderRadius: 3 }
      ] },
      options: { maintainAspectRatio: false, scales: axes("Average child poverty rate (%)"),
        plugins: { legend, tooltip: { callbacks: { label: (i) => `${i.dataset.label}: ${pct(i.raw)} (${i.dataset.counts[i.dataIndex]} ${label})` } } } }
    });

    draw("size-share-chart", {
      type: "bar",
      data: { labels, datasets: [
        { label: "With available meetings", data: tiers.map((t) => t.s.shareWith), counts: tiers.map((t) => t.s.nWith), backgroundColor: accent },
        { label: "Without", data: tiers.map((t) => 100 - t.s.shareWith), counts: tiers.map((t) => t.s.nWithout), backgroundColor: accent2 }
      ] },
      options: { maintainAspectRatio: false,
        scales: { x: { stacked: true, ticks: { color: text }, grid: { display: false } },
                  y: { stacked: true, max: 100, title: { display: true, text: "Share of districts (%)", color: text }, ticks: { color: text }, grid: { color: grid } } },
        plugins: { legend, tooltip: { callbacks: { label: (i) => `${i.dataset.label}: ${pct(i.raw)} (${i.dataset.counts[i.dataIndex]} ${label})` } } } }
    });

    draw("size-meetings-chart", {
      type: "bar",
      data: { labels, datasets: [{ label: "Average available meetings", data: tiers.map((t) => t.s.avgMeetings), counts: tiers.map((t) => t.s.n), backgroundColor: accent, borderRadius: 3 }] },
      options: { maintainAspectRatio: false, scales: axes("Average available meetings"),
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (i) => `${i.raw.toFixed(2)} meetings on average (${i.dataset.counts[i.dataIndex]} ${label})` } } } }
    });
  }

  const fmt = (n) => (Math.abs(n) >= 1000 ? n.toLocaleString(undefined, { maximumFractionDigits: 0 })
                                          : n.toLocaleString(undefined, { maximumFractionDigits: 1 }));

  const fmtCol = (c, n) => (current.percent.has(c) ? `${n.toFixed(1)}%` : fmt(n));

  function cell(c, v) {
    if (!current.numeric.has(c) || String(v ?? "").trim() === "") return v ?? "";
    return current.percent.has(c) ? `${toNumber(v).toFixed(2)}%` : toNumber(v).toLocaleString();
  }

  function renderStats() {
    const el = $("stats");
    el.innerHTML = "";
    const add = (label, value, sub) => {
      const d = document.createElement("div");
      d.className = "stat";
      d.innerHTML = `<div class="label"></div><div class="value"></div>${sub ? '<div class="sub"></div>' : ""}`;
      d.querySelector(".label").textContent = label;
      d.querySelector(".value").textContent = value;
      if (sub) d.querySelector(".sub").textContent = sub;
      el.appendChild(d);
    };
    add((current && current.recordLabel) || cfg.recordLabel || "Records", current.rows.length.toLocaleString());
    [...current.numeric].slice(0, 5).forEach((c) => {
      const vals = current.rows.map((r) => toNumber(r[c])).filter((v) => !isNaN(v));
      if (!vals.length) return add(`Average ${c}`, "–", "not available for these districts");
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      const missing = current.rows.length - vals.length;
      add(`Average ${c}`, fmtCol(c, avg), `range ${fmtCol(c, Math.min(...vals))} – ${fmtCol(c, Math.max(...vals))}` +
        (missing ? ` · ${missing.toLocaleString()} without a figure` : ""));
    });
    renderCompare();
  }

  const canCompare = () => { const c = cmpFor(current); return c && current.numeric.has(c.by) && current.numeric.has(c.metric); };

  function renderCompare() {
    const el = $("compare");
    el.hidden = !canCompare();
    renderUrban();
    if (el.hidden) return;
    fillCompare($("compare-body"), current.rows);
    $("compare-title").textContent = cmpFor(current).title;
  }

  // Splits rows into "value > 0" vs "value = 0" on cfg.compare.by and compares cfg.compare.metric.
  function fillCompare(body, allRows) {
    const cmp = cmpFor(current);
    const rows = allRows.filter((r) => !isNaN(toNumber(r[cmp.metric])));
    const groups = [
      { label: cmp.withLabel, rows: rows.filter((r) => toNumber(r[cmp.by]) > 0) },
      { label: cmp.withoutLabel, rows: rows.filter((r) => toNumber(r[cmp.by]) === 0) }
    ];
    body.innerHTML = "";
    groups.forEach((g) => {
      const vals = g.rows.map((r) => toNumber(r[cmp.metric])).filter((v) => !isNaN(v));
      const avg = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : NaN;
      const d = document.createElement("div");
      d.className = "stat";
      d.innerHTML = '<div class="label"></div><div class="value"></div><div class="sub"></div>';
      d.querySelector(".label").textContent = g.label;
      d.querySelector(".value").textContent = isNaN(avg) ? "None" : fmtCol(cmp.metric, avg);
      const label = ((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase();
      d.querySelector(".sub").textContent = g.rows.length
        ? `average ${cmp.metric.toLowerCase()} · ${g.rows.length.toLocaleString()} ${g.rows.length === 1 ? label.replace(/s$/, "") : label}`
        : `no ${label} in this group`;
      body.appendChild(d);
    });
  }

  // Urban-only section: shown when the data has a column named in cfg.urban.columns.
  function urbanColumn() {
    const names = ((cfg.urban && cfg.urban.columns) || []).map((n) => n.toLowerCase());
    return current.columns.find((c) => names.includes(c.trim().toLowerCase()));
  }

  // Urban and suburban both count: "Urban"/"Suburban", "Yes"/"True"/"1"/"X",
  // or an NCES locale such as "City: Large" or "21 - Suburb: Large".
  function isUrban(v) {
    const s = String(v ?? "").trim().toLowerCase();
    return ["yes", "y", "true", "1", "x", "urban", "suburban"].includes(s) || /\b(city|suburb)\b/.test(s) || /urban$/.test(s);
  }

  // Urban only (no suburbs): "Urban", or an NCES "City" locale such as "City: Large".
  function isCity(v) {
    const s = String(v ?? "").trim().toLowerCase();
    return s === "urban" || s === "large urban" || /\bcity\b/.test(s);
  }

  function renderUrban() {
    renderSubset("urban", isUrban, "are urban or suburban");
    renderSubset("city", isCity, "are urban, not counting suburban");
  }

  // Fills the section with id `id`: with/without comparison plus a scatter plot,
  // for the rows whose urban column passes `test`.
  function renderSubset(id, test, noteText) {
    const col = urbanColumn(), el = $(id);
    el.hidden = !col || !canCompare();
    $(`${id}-link`).hidden = el.hidden;
    if (el.hidden) return;
    const rows = current.rows.filter((r) => test(r[col]));
    fillCompare($(`${id}-body`), rows);
    $(`${id}-note`).textContent = `${rows.length.toLocaleString()} of ${current.rows.length.toLocaleString()} ${((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase()} ${noteText} (“${col}” column).`;
    const x = cmpFor(current).metric, y = cmpFor(current).by;
    const accent = cssVar("--accent"), text = cssVar("--muted"), grid = cssVar("--border");
    if (subsetCharts[id]) subsetCharts[id].destroy();
    const points = rows.map((r) => ({ x: toNumber(r[x]), y: toNumber(r[y]), m: toNumber(r[y]), name: rowLabel(r) }))
      .filter((p) => !isNaN(p.x) && !isNaN(p.y));
    const fit = fitLines(points, x, y);
    subsetCharts[id] = new Chart($(`${id}-chart`), {
      type: "scatter",
      data: { datasets: [{ label: `${y} vs ${x}`, data: points,
        backgroundColor: accent + "99", pointRadius: 4, pointHoverRadius: 6, order: 1 }, ...(fit ? fit.datasets : [])] },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          subtitle: fitSubtitle(fit, text),
          tooltip: { filter: (item) => !item.dataset.fit, callbacks: {
            title: (items) => items[0].raw.name,
            label: (item) => [`${x}: ${fmtCol(x, item.raw.x)}`, `${y}: ${fmtCol(y, item.raw.y)}`]
          } }
        },
        scales: {
          x: { type: "linear", title: { display: true, text: x, color: text }, ticks: { color: text }, grid: { color: grid } },
          y: { title: { display: true, text: y, color: text }, ticks: { color: text }, grid: { color: grid }, beginAtZero: true,
               min: points.every((p) => p.y >= 0) ? 0 : undefined }
        }
      }
    });
  }

  // District name for chart tooltips, with the state when the data has one.
  function rowLabel(r) {
    const nameCol = current.columns.find((c) => !current.numeric.has(c));
    const name = nameCol ? r[nameCol] : "";
    const place = ["State", "Province"].find((c) => current.columns.includes(c) && nameCol !== c);
    return place ? `${name}, ${r[place]}` : name;
  }

  function setupChartControls() {
    const nums = [...current.numeric];
    const section = $("chart-section");
    if (!nums.length) { section.hidden = true; return; }
    section.hidden = false;
    const fill = (sel, cols, pick) => {
      sel.innerHTML = "";
      cols.forEach((c) => sel.add(new Option(c, c, false, c === pick)));
    };
    const labelCol = current.columns.find((c) => !current.numeric.has(c)) || current.columns[0];
    const def = current.chart || cfg.chart || {};
    const has = (c) => current.columns.includes(c);
    if (def.type) $("chart-type").value = def.type;
    fill($("x-col"), current.columns, has(def.x) ? def.x : labelCol);
    fill($("y-col"), nums, has(def.y) ? def.y : nums.find((c) => c !== labelCol) || nums[0]);
    renderChart();
  }

  // Least-squares line of best fit through scatter points: a line dataset for Chart.js and the
  // equation (with R² and the number of points) for the chart's subtitle.
  const sig = (v) => {
    const a = Math.abs(v);
    if (a === 0) return "0";
    return (a >= 100 ? v.toFixed(0) : a >= 1 ? v.toFixed(2) : String(Number(v.toPrecision(3)))).replace(/^-/, "−");
  };

  function bestFit(points, xName, yName, opts = {}) {
    const pts = points.filter((p) => isFinite(p.x) && isFinite(p.y));
    const n = pts.length;
    if (n < 2) return null;
    const mx = pts.reduce((t, p) => t + p.x, 0) / n, my = pts.reduce((t, p) => t + p.y, 0) / n;
    let sxx = 0, sxy = 0, syy = 0;
    pts.forEach((p) => { sxx += (p.x - mx) ** 2; sxy += (p.x - mx) * (p.y - my); syy += (p.y - my) ** 2; });
    if (!sxx) return null;
    const m = sxy / sxx, b = my - m * mx, r2 = syy ? (sxy * sxy) / (sxx * syy) : 1;
    const xs = pts.map((p) => p.x), lo = Math.min(...xs), hi = Math.max(...xs);
    return {
      dataset: { type: "line", label: opts.label || "Line of best fit", fit: true, data: [{ x: lo, y: m * lo + b }, { x: hi, y: m * hi + b }],
        borderColor: opts.color || cssVar("--accent-2"), backgroundColor: opts.color || cssVar("--accent-2"), borderWidth: 2.5,
        borderDash: opts.dash || [], pointRadius: 0, pointHoverRadius: 0, fill: false, order: 0 },
      subtitle: [
        `${opts.title || "Line of best fit"}: ${yName} = ${sig(m)} × ${xName} ${b < 0 ? "−" : "+"} ${sig(Math.abs(b))}`,
        `R² ${r2 > 0 && r2 < 0.001 ? "< 0.001" : `= ${r2.toFixed(3)}`} (0 = no fit, 1 = perfect fit) · ${n.toLocaleString()} ${((current && current.recordLabel) || cfg.recordLabel || "points").toLowerCase()}`
      ]
    };
  }

  const fitSubtitle = (fit, color) => (fit
    ? { display: true, text: fit.subtitle, color, font: { size: 12 }, padding: { bottom: 10 } }
    : { display: false });

  // Lines of best fit for a scatter plot: one through every point, and, when the chart uses the
  // meeting counts, a second (dashed) one through only the districts with 1+ meetings, since the
  // many 0s pull the first line down. Points carry `m`, their meeting count.
  function fitLines(points, x, y) {
    const all = bestFit(points, x, y);
    if (!all) return null;
    const by = cmpFor(current).by;
    const label = ((current && current.recordLabel) || cfg.recordLabel || "districts").toLowerCase();
    const withM = points.filter((p) => p.m > 0);
    const some = (x === by || y === by) && withM.length >= 2 && withM.length < points.length;
    const only = some && bestFit(withM, x, y, { label: `Line of best fit (${label} with meetings only)`,
      title: `Dashed line, ${label} with 1+ meetings only`, color: cssVar("--text"), dash: [7, 5] });
    if (!only) return { datasets: [all.dataset], subtitle: all.subtitle };
    return { datasets: [all.dataset, only.dataset],
      subtitle: [`Solid line, all ${label}: ${all.subtitle[0].replace(/^Line of best fit: /, "")}`, all.subtitle[1], ...only.subtitle] };
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function renderChart() {
    const x = $("x-col").value, y = $("y-col").value, type = $("chart-type").value;
    const limit = Number($("chart-limit").value);
    let rows = current.rows.filter((r) => !isNaN(toNumber(r[y])));
    const xIsNum = current.numeric.has(x);
    $("chart-limit").disabled = type === "scatter";
    $("chart-type").querySelector('[value="scatter"]').disabled = !xIsNum;
    if (type === "scatter" && !xIsNum) { $("chart-type").value = "bar"; return renderChart(); }
    if (type !== "scatter") {
      rows = [...rows].sort((a, b) => toNumber(b[y]) - toNumber(a[y]));
      if (limit) rows = rows.slice(0, limit);
    }
    const accent = cssVar("--accent"), text = cssVar("--muted"), grid = cssVar("--border");
    let data, fit = null, yMin;
    if (type === "scatter") {
      const points = rows.map((r) => ({ x: toNumber(r[x]), y: toNumber(r[y]), m: toNumber(r[cmpFor(current).by]), name: rowLabel(r) }))
        .filter((p) => !isNaN(p.x));
      fit = fitLines(points, x, y);
      if (points.every((p) => p.y >= 0)) yMin = 0;   // keep the axis at 0; the fit line is clipped there
      data = { datasets: [{ label: `${y} vs ${x}`, data: points,
        backgroundColor: accent + "99", pointRadius: 3.5, pointHoverRadius: 6, order: 1 }, ...(fit ? fit.datasets : [])] };
    } else {
      data = { labels: rows.map((r) => (current.numeric.has(x) ? cell(x, r[x]) : r[x])),
        datasets: [{ label: y, data: rows.map((r) => toNumber(r[y])),
          backgroundColor: accent, borderColor: accent, borderRadius: 3, tension: 0.2 }] };
    }
    if (chart) chart.destroy();
    chart = new Chart($("chart"), {
      type, data,
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          subtitle: fitSubtitle(fit, text),
          tooltip: { filter: (item) => !item.dataset.fit, callbacks: {
            title: (items) => (type === "scatter" ? items[0].raw.name : items[0].label),
            label: (item) => type === "scatter"
              ? [`${x}: ${fmtCol(x, item.raw.x)}`, `${y}: ${fmtCol(y, item.raw.y)}`]
              : `${y}: ${fmtCol(y, item.raw)}`
          } }
        },
        scales: {
          x: { type: type === "scatter" ? "linear" : "category", title: { display: true, text: x, color: text },
               ticks: { color: text, maxRotation: 60, autoSkip: true }, grid: { color: grid } },
          y: { title: { display: true, text: y, color: text }, ticks: { color: text }, grid: { color: grid }, beginAtZero: type === "bar", min: yMin }
        }
      }
    });
  }

  // Filters bar (Overview and Map): locale, meetings, poverty range and size tier. The data
  // table, its download and the map follow them; the summary cards and charts don't.
  const filterInputs = ["f-locale", "f-meetings", "f-pov-min", "f-pov-max", "f-size"];
  const filterValue = (id) => $(id).value.trim();
  const filtersActive = () => filterInputs.some((id) => filterValue(id) !== "");

  function passesFilters(r) {
    const locale = filterValue("f-locale"), meetings = filterValue("f-meetings"), size = filterValue("f-size");
    const min = filterValue("f-pov-min"), max = filterValue("f-pov-max");
    if (locale && String(r.Locale || "").trim() !== locale) return false;
    if (meetings) {
      const m = toNumber(r[cmpFor(current).by]);
      if (meetings === "with" ? !(m > 0) : m > 0) return false;
    }
    if (min !== "" || max !== "") {
      const p = toNumber(r[cmpFor(current).metric]);
      if (isNaN(p) || (min !== "" && p < Number(min)) || (max !== "" && p > Number(max))) return false;
    }
    if (size) {
      const t = cfg.sizeTiers.tiers.find((x) => x.name === size), e = toNumber(r[cfg.sizeTiers.column]);
      if (isNaN(e) || e < t.min || (t.max != null && e > t.max)) return false;
    }
    return true;
  }

  function applyFilters() {
    renderTable();
    const n = current.rows.filter(passesFilters).length;
    $("f-status").textContent = filtersActive()
      ? `${n.toLocaleString()} of ${current.rows.length.toLocaleString()} ${((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase()} match. The data table, its download and the map show only these; the summary figures and charts above use all ${((current && current.recordLabel) || cfg.recordLabel || "records").toLowerCase()}.`
      : "";
    if (window.SiteMap) window.SiteMap.restyle();
  }

  function setupFilters() {
    cfg.sizeTiers.tiers.forEach((t) => $("f-size").add(new Option(
      `${t.name} (${t.max == null ? `${t.min.toLocaleString()}+` : `${t.min.toLocaleString()}–${t.max.toLocaleString()}`} students)`, t.name)));
    filterInputs.forEach((id) => $(id).addEventListener("input", applyFilters));
    $("f-clear").addEventListener("click", () => { filterInputs.forEach((id) => { $(id).value = ""; }); applyFilters(); });
    window.SiteFilters = { active: filtersActive, test: passesFilters };
  }

  function visibleRows() {
    const q = $("search").value.trim().toLowerCase();
    let rows = current.rows.filter(passesFilters);
    if (q) rows = rows.filter((r) => current.columns.some((c) => String(r[c] ?? "").toLowerCase().includes(q)));
    if (sort.col) {
      const c = sort.col, isNum = current.numeric.has(c);
      // Blank cells always sort last.
      rows = [...rows].sort((a, b) => {
        const ea = String(a[c] ?? "").trim() === "", eb = String(b[c] ?? "").trim() === "";
        if (ea || eb) return ea - eb;
        if (isNum) return (toNumber(a[c]) - toNumber(b[c])) * sort.dir;
        return String(a[c] ?? "").localeCompare(String(b[c] ?? ""), undefined, { numeric: true }) * sort.dir;
      });
    }
    return rows;
  }

  function renderTable() {
    const thead = $("table").tHead, tbody = $("table").tBodies[0];
    thead.innerHTML = "";
    const tr = thead.insertRow();
    current.columns.forEach((c) => {
      const th = document.createElement("th");
      th.textContent = c + " ";
      const arrow = document.createElement("span");
      arrow.className = "arrow";
      arrow.textContent = sort.col === c ? (sort.dir > 0 ? "▲" : "▼") : "↕";
      th.appendChild(arrow);
      th.addEventListener("click", () => {
        sort = { col: c, dir: sort.col === c ? -sort.dir : 1 };
        renderTable();
      });
      tr.appendChild(th);
    });
    const matching = visibleRows();
    const rows = matching.slice(0, TABLE_LIMIT);
    tbody.innerHTML = "";
    const frag = document.createDocumentFragment();
    rows.forEach((r) => {
      const row = document.createElement("tr");
      current.columns.forEach((c) => {
        const td = document.createElement("td");
        const v = r[c] ?? "";
        if (/^https?:\/\/\S+$/.test(String(v).trim())) {
          const a = document.createElement("a");
          a.href = String(v).trim(); a.textContent = "Link"; a.target = "_blank"; a.rel = "noopener";
          td.appendChild(a);
        } else {
          td.textContent = cell(c, v);
        }
        if (current.numeric.has(c)) td.className = "num";
        row.appendChild(td);
      });
      frag.appendChild(row);
    });
    tbody.appendChild(frag);
    $("row-count").textContent = matching.length > rows.length
      ? `Showing the first ${rows.length.toLocaleString()} of ${matching.length.toLocaleString()} matching rows (${current.rows.length.toLocaleString()} in total). Search or sort to find others; “Download CSV” gets them all.`
      : `Showing ${rows.length.toLocaleString()} of ${current.rows.length.toLocaleString()} rows`;
  }

  function download() {
    const csv = Papa.unparse({ fields: current.columns, data: visibleRows().map((r) => current.columns.map((c) => r[c])) });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = `${current.name.replace(/\W+/g, "-").toLowerCase()}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  // Rules table: US state rules, or Canada's provincial ones in the Canada views (both in "All").
  function renderRules() {
    const us = window.STATE_RULES;
    if (!us) return;
    const ca = us.canada;
    const isCA = current && (current.country === "CA" || (current.parent && current.parent.country === "CA"));
    const both = current && current.combined;
    const laws = isCA ? ca.laws : both ? [...us.laws, ...ca.laws] : us.laws;
    $("rules-title").textContent = isCA ? "Province rules for recording or streaming school board meetings (Canada)"
      : both ? "State and province rules for recording or streaming school board meetings (US and Canada)"
      : "State rules for recording or streaming school board meetings";
    $("rules-place").textContent = isCA ? "Province" : both ? "State or province" : "State";
    $("rules-intro").textContent = isCA
      ? `No province requires school boards to record or stream meetings; ${laws.length} related rules in ${new Set(laws.map((x) => x.state)).size} provinces, checked ${ca.checked}.`
      : `${us.laws.length} rules in ${new Set(us.laws.map((x) => x.state)).size} states, checked ${us.checked}` +
        (both ? `; ${ca.laws.length} related rules in Canadian provinces, checked ${ca.checked}` : "") + ". Laws change often.";
    $("rules-us-note").hidden = isCA;
    $("rules-ca-note").hidden = !isCA && !both;
    $("rules-ca-note").textContent = ca.note;
    const body = $("rules-table").tBodies[0];
    body.innerHTML = "";
    laws.forEach((x) => {
      const tr = body.insertRow();
      [x.state, x.covers, x.threshold || "None (all boards)", x.rule].forEach((v) => { tr.insertCell().textContent = v; });
    });
    $("rules-proposed-card").hidden = isCA;
    const ul = $("rules-proposed");
    ul.innerHTML = "";
    us.proposed.forEach((x) => {
      const li = document.createElement("li");
      const b = document.createElement("strong");
      b.textContent = `${x.state}: `;
      li.append(b, x.note);
      ul.appendChild(li);
    });
    const label = isCA ? "Province rules" : both ? "State & province rules" : "State rules";
    document.querySelectorAll('[data-view-tab="rules"], [data-view-link="rules"]').forEach((el) => { el.textContent = label; });
  }

  // Sources for the selected dataset: entries marked `only` (a name or a list of names)
  // show just for those datasets. A state's view also shows entries marked with its name.
  function renderSources() {
    const box = $("sources-list");
    box.innerHTML = "";
    const shown = (x) => !x.only || [].concat(x.only).some((n) => n === (current.sourcesAs || current.name) || n === current.name);
    // Groups with no `only` are about the US data; another country's view shows only its own groups.
    const other = current.country || (current.parent && current.parent.country);
    const keep = (x) => current.combined || shown(x);
    (window.SOURCES || []).filter((g) => current.combined || ((other ? !!g.only : true) && shown(g))).forEach((g) => {
      const items = g.items.filter(keep);
      if (!items.length) return;
      const h = document.createElement("h3");
      h.textContent = g.group;
      const ul = document.createElement("ul");
      items.forEach((s) => {
        const li = document.createElement("li");
        if (s.url) {
          const a = document.createElement("a");
          a.href = s.url; a.textContent = s.title || s.url; a.target = "_blank"; a.rel = "noopener";
          li.appendChild(a);
        } else {
          li.textContent = s.title;
        }
        ul.appendChild(li);
      });
      box.append(h, ul);
      if (g.note) {
        const p = document.createElement("p");
        p.className = "note";
        p.textContent = `Note: ${g.note}`;
        box.appendChild(p);
      }
    });
  }

  $("search").addEventListener("input", renderTable);
  $("download").addEventListener("click", download);
  ["x-col", "y-col", "chart-type", "chart-limit"].forEach((id) => $(id).addEventListener("change", renderChart));
  document.querySelectorAll("[data-view-tab]").forEach((b) => b.addEventListener("click", () => {
    setView(b.dataset.viewTab);
    history.replaceState(null, "", b.dataset.viewTab === "overview" ? location.pathname + location.search : `#${b.dataset.viewTab}`);
  }));
  // Header links: "By district size" and "Sources" open those views; the others jump to a section of the overview.
  document.querySelectorAll(".links a").forEach((a) => a.addEventListener("click", () => {
    setView(a.dataset.viewLink || "overview");
  }));
  const viewFromHash = () => { if (["#size", "#locale", "#map", "#rules", "#sources"].includes(location.hash)) setView(location.hash.slice(1)); };
  viewFromHash();
  window.addEventListener("hashchange", viewFromHash);
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (!current) return;
    renderChart();
    renderUrban();
    if (view === "size") renderSize();
    if (view === "locale") renderLocale();
  });

  load();
})();
