(function () {
  const cfg = window.SITE_CONFIG;
  const $ = (id) => document.getElementById(id);
  let datasets = [];   // [{ name, columns, rows, numeric: Set }]
  let current = null;
  let sort = { col: null, dir: 1 };
  let chart = null;
  const subsetCharts = {};

  document.title = cfg.title;
  $("site-title").textContent = cfg.title;
  $("sources-link").href = cfg.sourcesUrl;
  renderSources();

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

  function parse(name, text) {
    const out = Papa.parse(text, { header: true, skipEmptyLines: "greedy" });
    const filled = (v) => String(v ?? "").trim() !== "";
    let columns = (out.meta.fields || []).filter((c) => c && c.trim() !== "");
    const rows = out.data.filter((r) => columns.some((c) => filled(r[c])));
    columns = columns.filter((c) => rows.some((r) => filled(r[c])));
    const numeric = new Set(columns.filter((c) => {
      const vals = rows.map((r) => r[c]).filter(filled);
      return vals.length > 0 && vals.every((v) => !isNaN(toNumber(v)));
    }));
    const percent = new Set([...numeric].filter((c) =>
      rows.map((r) => r[c]).filter(filled).every((v) => String(v).trim().endsWith("%"))));
    return { name, columns, rows, numeric, percent };
  }

  async function load() {
    try {
      datasets = await Promise.all(cfg.dataFiles.map(async (d) => parse(d.name, await fetchCsv(d.file))));
      $("status").textContent = "";
    } catch (err) {
      $("status").classList.add("error");
      $("status").textContent = `Couldn't load the data (${err.message}). Please try again later.`;
      return;
    }
    renderTabs();
    select(0);
  }

  function renderTabs() {
    const tabs = $("tabs");
    tabs.hidden = datasets.length < 2;
    tabs.innerHTML = "";
    datasets.forEach((d, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.role = "tab";
      b.textContent = d.name;
      b.addEventListener("click", () => select(i));
      tabs.appendChild(b);
    });
  }

  function select(i) {
    current = datasets[i];
    sort = { col: null, dir: 1 };
    [...$("tabs").children].forEach((b, j) => b.setAttribute("aria-selected", String(i === j)));
    $("search").value = "";
    renderStats();
    setupChartControls();
    renderTable();
    $("table-section").hidden = false;
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
    add(cfg.recordLabel || "Records", current.rows.length.toLocaleString());
    [...current.numeric].slice(0, 5).forEach((c) => {
      const vals = current.rows.map((r) => toNumber(r[c])).filter((v) => !isNaN(v));
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      add(`Average ${c}`, fmtCol(c, avg), `range ${fmtCol(c, Math.min(...vals))} – ${fmtCol(c, Math.max(...vals))}`);
    });
    renderCompare();
  }

  const canCompare = () => cfg.compare && current.numeric.has(cfg.compare.by) && current.numeric.has(cfg.compare.metric);

  function renderCompare() {
    const el = $("compare");
    el.hidden = !canCompare();
    if (el.hidden) return;
    fillCompare($("compare-body"), current.rows);
    $("compare-title").textContent = cfg.compare.title;
    renderUrban();
  }

  // Splits rows into "value > 0" vs "value = 0" on cfg.compare.by and compares cfg.compare.metric.
  function fillCompare(body, rows) {
    const cmp = cfg.compare;
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
      d.querySelector(".value").textContent = isNaN(avg) ? "–" : fmtCol(cmp.metric, avg);
      d.querySelector(".sub").textContent = `average ${cmp.metric.toLowerCase()} · ${g.rows.length.toLocaleString()} ${(cfg.recordLabel || "records").toLowerCase()}`;
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
    return ["yes", "y", "true", "1", "x", "urban", "suburban"].includes(s) || /\b(city|suburb)\b/.test(s);
  }

  // Urban only (no suburbs): "Urban", or an NCES "City" locale such as "City: Large".
  function isCity(v) {
    const s = String(v ?? "").trim().toLowerCase();
    return s === "urban" || /\bcity\b/.test(s);
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
    $(`${id}-note`).textContent = `${rows.length.toLocaleString()} of ${current.rows.length.toLocaleString()} ${(cfg.recordLabel || "records").toLowerCase()} ${noteText} (“${col}” column).`;
    const x = cfg.compare.metric, y = cfg.compare.by;
    const nameCol = current.columns.find((c) => !current.numeric.has(c));
    const accent = cssVar("--accent"), text = cssVar("--muted"), grid = cssVar("--border");
    if (subsetCharts[id]) subsetCharts[id].destroy();
    subsetCharts[id] = new Chart($(`${id}-chart`), {
      type: "scatter",
      data: { datasets: [{ label: `${y} vs ${x}`,
        data: rows.map((r) => ({ x: toNumber(r[x]), y: toNumber(r[y]), name: nameCol ? r[nameCol] : "" }))
          .filter((p) => !isNaN(p.x) && !isNaN(p.y)),
        backgroundColor: accent + "99", pointRadius: 4, pointHoverRadius: 6 }] },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: {
            title: (items) => items[0].raw.name,
            label: (item) => [`${x}: ${fmtCol(x, item.raw.x)}`, `${y}: ${fmtCol(y, item.raw.y)}`]
          } }
        },
        scales: {
          x: { type: "linear", title: { display: true, text: x, color: text }, ticks: { color: text }, grid: { color: grid } },
          y: { title: { display: true, text: y, color: text }, ticks: { color: text }, grid: { color: grid }, beginAtZero: true }
        }
      }
    });
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
    const def = cfg.chart || {};
    const has = (c) => current.columns.includes(c);
    if (def.type) $("chart-type").value = def.type;
    fill($("x-col"), current.columns, has(def.x) ? def.x : labelCol);
    fill($("y-col"), nums, has(def.y) ? def.y : nums.find((c) => c !== labelCol) || nums[0]);
    renderChart();
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function renderChart() {
    const x = $("x-col").value, y = $("y-col").value, type = $("chart-type").value;
    const limit = Number($("chart-limit").value);
    const nameCol = current.columns.find((c) => !current.numeric.has(c));
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
    let data;
    if (type === "scatter") {
      data = { datasets: [{ label: `${y} vs ${x}`,
        data: rows.map((r) => ({ x: toNumber(r[x]), y: toNumber(r[y]), name: nameCol ? r[nameCol] : "" }))
          .filter((p) => !isNaN(p.x)),
        backgroundColor: accent + "99", pointRadius: 3.5, pointHoverRadius: 6 }] };
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
          tooltip: { callbacks: {
            title: (items) => (type === "scatter" ? items[0].raw.name : items[0].label),
            label: (item) => type === "scatter"
              ? [`${x}: ${fmtCol(x, item.raw.x)}`, `${y}: ${fmtCol(y, item.raw.y)}`]
              : `${y}: ${fmtCol(y, item.raw)}`
          } }
        },
        scales: {
          x: { type: type === "scatter" ? "linear" : "category", title: { display: true, text: x, color: text },
               ticks: { color: text, maxRotation: 60, autoSkip: true }, grid: { color: grid } },
          y: { title: { display: true, text: y, color: text }, ticks: { color: text }, grid: { color: grid }, beginAtZero: type === "bar" }
        }
      }
    });
  }

  function visibleRows() {
    const q = $("search").value.trim().toLowerCase();
    let rows = current.rows;
    if (q) rows = rows.filter((r) => current.columns.some((c) => String(r[c] ?? "").toLowerCase().includes(q)));
    if (sort.col) {
      const c = sort.col, isNum = current.numeric.has(c);
      rows = [...rows].sort((a, b) => {
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
    const rows = visibleRows();
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
    $("row-count").textContent = `Showing ${rows.length.toLocaleString()} of ${current.rows.length.toLocaleString()} rows`;
  }

  function download() {
    const csv = Papa.unparse({ fields: current.columns, data: visibleRows().map((r) => current.columns.map((c) => r[c])) });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = `${current.name.replace(/\W+/g, "-").toLowerCase()}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function renderSources() {
    const box = $("sources-list");
    (window.SOURCES || []).forEach((g) => {
      const h = document.createElement("h3");
      h.textContent = g.group;
      const ul = document.createElement("ul");
      g.items.forEach((s) => {
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
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (!current) return;
    renderChart();
    renderUrban();
  });

  load();
})();
