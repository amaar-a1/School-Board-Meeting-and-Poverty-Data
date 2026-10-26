(function () {
  const cfg = window.SITE_CONFIG;
  const $ = (id) => document.getElementById(id);
  let datasets = [];   // [{ name, columns, rows, numeric: Set }]
  let current = null;
  let sort = { col: null, dir: 1 };
  let chart = null;

  document.title = cfg.title;
  $("site-title").textContent = cfg.title;
  $("sources-link").href = cfg.sourcesUrl;
  $("sheet-link").href = cfg.spreadsheetUrl;
  renderSources();

  function sheetUrl(name) {
    let url = `https://docs.google.com/spreadsheets/d/${cfg.sheetId}/gviz/tq?tqx=out:csv`;
    if (name) url += `&sheet=${encodeURIComponent(name)}`;
    return url;
  }

  async function fetchCsv(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    if (text.trim().startsWith("<")) throw new Error("Sheet is not publicly viewable");
    return text;
  }

  function toNumber(v) {
    if (v == null) return NaN;
    const s = String(v).trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  }

  function parse(name, text) {
    const out = Papa.parse(text, { header: true, skipEmptyLines: "greedy" });
    const columns = (out.meta.fields || []).filter((c) => c && c.trim() !== "");
    const rows = out.data.filter((r) => columns.some((c) => String(r[c] ?? "").trim() !== ""));
    const numeric = new Set(columns.filter((c) => {
      const vals = rows.map((r) => r[c]).filter((v) => String(v ?? "").trim() !== "");
      return vals.length > 0 && vals.every((v) => !isNaN(toNumber(v)));
    }));
    return { name, columns, rows, numeric };
  }

  async function load() {
    const names = cfg.sheets && cfg.sheets.length ? cfg.sheets : [null];
    try {
      datasets = await Promise.all(names.map(async (n) => parse(n || "Data", await fetchCsv(sheetUrl(n)))));
      $("status").textContent = "";
    } catch (err) {
      try {
        datasets = [parse("Data", await fetchCsv(cfg.fallbackCsv))];
        $("status").textContent = "Showing a saved copy of the data (the live spreadsheet couldn't be reached).";
      } catch (_) {
        $("status").classList.add("error");
        $("status").innerHTML = `Couldn't load the spreadsheet (${err.message}). Make sure it is shared as
          “Anyone with the link can view”, or <a href="${cfg.spreadsheetUrl}" target="_blank" rel="noopener">open it directly</a>.`;
        return;
      }
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
                                          : n.toLocaleString(undefined, { maximumFractionDigits: 2 }));

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
    add("Records", current.rows.length.toLocaleString());
    [...current.numeric].slice(0, 5).forEach((c) => {
      const vals = current.rows.map((r) => toNumber(r[c])).filter((v) => !isNaN(v));
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      add(`Average ${c}`, fmt(avg), `range ${fmt(Math.min(...vals))} – ${fmt(Math.max(...vals))}`);
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
    fill($("x-col"), current.columns, labelCol);
    fill($("y-col"), nums, nums.find((c) => c !== labelCol) || nums[0]);
    renderChart();
  }

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function renderChart() {
    const x = $("x-col").value, y = $("y-col").value, type = $("chart-type").value;
    const rows = current.rows.filter((r) => !isNaN(toNumber(r[y])));
    const accent = cssVar("--accent"), text = cssVar("--muted"), grid = cssVar("--border");
    let data;
    if (type === "scatter") {
      data = { datasets: [{ label: `${y} vs ${x}`,
        data: rows.map((r) => ({ x: toNumber(r[x]), y: toNumber(r[y]), label: r[x] })).filter((p) => !isNaN(p.x)),
        backgroundColor: accent }] };
    } else {
      data = { labels: rows.map((r) => r[x]),
        datasets: [{ label: y, data: rows.map((r) => toNumber(r[y])),
          backgroundColor: accent, borderColor: accent, borderRadius: 3, tension: 0.2 }] };
    }
    if (chart) chart.destroy();
    chart = new Chart($("chart"), {
      type, data,
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
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
          td.textContent = v;
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
    const list = $("sources-list");
    (window.SOURCES || []).forEach((s) => {
      const li = document.createElement("li");
      if (s.url) {
        const a = document.createElement("a");
        a.href = s.url; a.textContent = s.title || s.url; a.target = "_blank"; a.rel = "noopener";
        li.appendChild(a);
      } else {
        li.textContent = s.title;
      }
      list.appendChild(li);
    });
  }

  $("search").addEventListener("input", renderTable);
  $("download").addEventListener("click", download);
  ["x-col", "y-col", "chart-type"].forEach((id) => $(id).addEventListener("change", renderChart));
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => current && renderChart());

  load();
})();
