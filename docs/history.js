// Line graphs over time, from the "... by year" columns ("2019: 9.7%; 2020: 9.8%; ..."): the Trends tab (averages or
// totals for the country shown, or one line per country in "All"), and one place's or two places' own lines (the Find
// card and Compare). One chart at a time, with a row of buttons to pick the measure, so the page stays uncluttered.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  // kind "rate": averaged over places; "count": added up over places (both linked year to year, see linked()).
  const MEASURES = [
    { col: "Poverty by year", name: "Poverty", axis: "Poverty rate (%)", kind: "rate", unit: "%" },
    { col: "Enrollment by year", name: "Enrollment", axis: "Pupils", kind: "count" },
    { col: "Public share by year", name: "Public schools' share", axis: "Pupils at public schools (%)", kind: "rate", unit: "%" },
    { col: "Population by year", name: "Population", axis: "People", kind: "count" },
    { col: "Meetings by year", name: "Meetings", axis: "Meetings recorded", kind: "count", place: true }
  ];
  // Colour-blind-safe (Okabe-Ito) for lines beyond the site's two accents.
  const PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#8c6d31", "#7f7f7f"];

  function parse(v) {
    const out = {};
    String(v || "").split(";").forEach((p) => {
      const i = p.indexOf(":"); if (i < 0) return;
      const y = p.slice(0, i).trim(), n = Number(p.slice(i + 1).replace(/[%,\s]/g, ""));
      if (/^\d{4}$/.test(y) && p.slice(i + 1).trim() !== "" && !isNaN(n)) out[y] = n;
    });
    return out;
  }
  const years = (m) => Object.keys(m).sort();
  const hasLine = (row, col) => years(parse(row[col])).length >= 2;
  const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;

  // A line for a group of places whose years don't all match: each year's change is measured on the places with a
  // figure in both years (the change in their total for counts, their average change in points for rates), and the
  // chain is pinned to the year most places have (that year's total or average over all of them). A place missing a
  // year so doesn't show as a fall, a place added later as a rise, nor a year that covers only some places (say,
  // cities only) as a jump in the average.
  function linked(series, kind) {
    const ys = [...new Set(series.flatMap(years))].sort();
    if (ys.length < 2) return {};
    // A year with no place in common with the one before (or nothing to scale from) starts a new stretch; only the
    // stretch holding the anchor year is drawn.
    const base = kind === "count" ? 1 : 0, lvl = { [ys[0]]: base }, seg = { [ys[0]]: 0 };
    for (let i = 1; i < ys.length; i++) {
      let a = 0, b = 0, n = 0;
      series.forEach((s) => { if (s[ys[i - 1]] != null && s[ys[i]] != null) { a += s[ys[i - 1]]; b += s[ys[i]]; n++; } });
      const ok = n > 0 && (kind !== "count" || a > 0);
      seg[ys[i]] = seg[ys[i - 1]] + (ok ? 0 : 1);
      lvl[ys[i]] = !ok ? base : kind === "count" ? lvl[ys[i - 1]] * b / a : lvl[ys[i - 1]] + (b - a) / n;
    }
    const cover = (y) => series.filter((s) => s[y] != null).length;
    const anchor = ys.reduce((best, y) => (cover(y) >= cover(best) ? y : best), ys[0]);
    const vals = series.map((s) => s[anchor]).filter((v) => v != null);
    const at = kind === "count" ? vals.reduce((t, v) => t + v, 0) : mean(vals);
    const keep = ys.filter((y) => seg[y] === seg[anchor]);
    const out = {};
    keep.forEach((y) => { out[y] = kind === "count" ? Math.round(at * lvl[y] / lvl[anchor]) : +(at + lvl[y] - lvl[anchor]).toFixed(2); });
    return keep.length > 1 ? out : {};
  }
  function summarize(rows, m) {
    const series = rows.map((r) => parse(r[m.col])).filter((s) => years(s).length);
    return { line: linked(series, m.kind), n: series.length };
  }

  const charts = new WeakMap();
  function draw(canvas, labels, datasets, axis, opts = {}) {
    if (charts.has(canvas)) charts.get(canvas).destroy();
    const text = cssVar("--muted"), grid = cssVar("--border");
    const fmt = (v) => (v == null ? "–" : opts.unit === "%" ? `${(+v).toFixed(1)}%` : Math.round(v).toLocaleString());
    const ch = new Chart(canvas, { type: "line",
      data: { labels, datasets: datasets.map((d) => ({ tension: 0.2, pointRadius: labels.length > 20 ? 2 : 4, spanGaps: true, borderWidth: 2, ...d })) },
      options: { maintainAspectRatio: false, animation: matchMedia("(prefers-reduced-motion: reduce)").matches ? false : undefined,
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: datasets.length > 1, labels: { color: text, boxWidth: 14 } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${opts.raw ? fmt(opts.raw[c.datasetIndex][c.label]) + ` (${c.parsed.y.toFixed(0)})` : fmt(c.parsed.y)}` } } },
        scales: { x: { ticks: { color: text }, grid: { color: grid } },
          y: { beginAtZero: !!opts.zero, title: { display: true, text: axis, color: text }, ticks: { color: text, callback: (v) => (opts.unit === "%" ? `${v}%` : Number(v).toLocaleString()) }, grid: { color: grid } } } } });
    charts.set(canvas, ch);
    canvas.setAttribute("aria-label", `Line chart: ${axis}, ${labels[0]}–${labels[labels.length - 1]}, ` + datasets.map((d) => `${d.label} ${fmt(d.data.find((v) => v != null))} to ${fmt([...d.data].reverse().find((v) => v != null))}`).join("; "));
    return ch;
  }

  // A row of buttons (one per measure with a line) above a chart; returns the measure picked.
  function picker(holder, list, chosen, onPick) {
    holder.innerHTML = list.map((m) => `<button type="button" aria-pressed="${m === chosen}" data-col="${esc(m.col)}">${esc(m.name)}</button>`).join("");
    holder.hidden = list.length < 2;
    holder.onclick = (e) => { const b = e.target.closest("button[data-col]"); if (b) onPick(list.find((m) => m.col === b.dataset.col)); };
  }

  // The Trends tab's "Over time" card.
  let trendMeasure = null;
  function renderTrends(current, label) {
    const rows = current.rows;
    const list = MEASURES.filter((m) => !m.place && rows.some((r) => hasLine(r, m.col)));
    const card = $("trend-history-card");
    if (!card) return;
    card.hidden = !list.length;
    $("trend-history-empty").hidden = !!list.length;
    if (!list.length) return;
    const m = list.includes(trendMeasure) ? trendMeasure : list[0];
    picker($("trend-history-pick"), list, m, (x) => { trendMeasure = x; renderTrends(current, label); });
    const canvas = $("trend-history");
    let note;
    if (current.combined) {
      // One line per country (the countries with the most places that have a line, up to eight); counts as an index.
      const byC = {};
      rows.forEach((r) => { if (hasLine(r, m.col)) (byC[r.Country] = byC[r.Country] || []).push(r); });
      const all = Object.entries(byC).sort((a, b) => b[1].length - a[1].length), top = all.slice(0, PALETTE.length);
      const lines = top.map(([c, rs]) => [c, summarize(rs, m).line]);
      const labels = [...new Set(lines.flatMap(([, l]) => years(l)))].sort();
      const idx = m.kind === "count";
      draw(canvas, labels, lines.map(([c, l], i) => {
        const first = l[years(l)[0]];
        return { label: c, borderColor: PALETTE[i], backgroundColor: PALETTE[i], data: labels.map((y) => (l[y] == null ? null : idx ? +(100 * l[y] / first).toFixed(1) : l[y])) };
      }), idx ? `${m.axis}, first year = 100` : m.axis, { unit: idx ? "" : m.unit, raw: idx ? lines.map(([, l]) => l) : null });
      note = `One line per country, each linked year to year over its places with figures in both years (${all.length} have ${m.name.toLowerCase()} for more than one year` + (all.length > top.length ? `; the ${top.length} with the most places are shown, and the others are under their own country` : "") + "). " +
        (idx ? "Each line starts at 100 in its country's first year, so lines of different sizes can be compared; hover to see the totals." : "Each country uses its own measure, so compare the shapes of the lines, not their heights.");
    } else {
      const { line, n } = summarize(rows, m);
      const labels = years(line);
      draw(canvas, labels, [{ label: m.name, borderColor: cssVar("--accent"), backgroundColor: cssVar("--accent"), data: labels.map((y) => line[y]) }], m.kind === "count" ? `${m.axis} (all ${label})` : `${m.axis}, average of ${label}`, { unit: m.unit, zero: m.kind === "rate" });
      note = (m.kind === "count" ? `The total for the ${n.toLocaleString()} ${label} with figures` : `The average of the ${n.toLocaleString()} ${label}' figures` + (m.col === "Poverty by year" ? " (the country's own measure, as in its note)" : "")) +
        ". Not every place has every year, so each year's change is measured on the places with figures in both years, and the line is pinned to the year most places have; a gap, or a year published for only some places, doesn't show as a rise or a fall.";
    }
    $("trend-history-note").textContent = note;
  }

  // One place's own lines (Find card), or two places' (Compare). entries: [{ name, row }].
  function renderPlaces(holder, entries, opts = {}) {
    entries = entries.filter(Boolean);
    const list = MEASURES.filter((m) => entries.some((e) => hasLine(e.row, m.col)));
    if (!list.length) { holder.hidden = true; holder.innerHTML = ""; return; }
    holder.hidden = false;
    const state = holder._m && list.includes(holder._m) ? holder._m : list[0];
    holder.innerHTML = `<h3 class="hist-title">${esc(opts.title || "Over time")}</h3><div class="hist-pick" role="group" aria-label="Measure"></div>` +
      `<div class="chart-box hist-box"><canvas role="img"></canvas></div><p class="note hist-note"></p>`;
    picker(holder.querySelector(".hist-pick"), list, state, (x) => { holder._m = x; renderPlaces(holder, entries, opts); });
    const m = state;
    const series = entries.map((e) => parse(e.row[m.col]));
    const labels = [...new Set(series.flatMap(years))].sort();
    const colors = [cssVar("--accent"), cssVar("--accent-2")];
    // Two places of very different sizes: an index (first shared year = 100), with the counts in the tooltip.
    const tops = series.map((s) => Math.max(0, ...Object.values(s)));
    const idx = m.kind === "count" && series.length === 2 && Math.min(...tops) > 0 && Math.max(...tops) / Math.min(...tops) > 4;
    const base = idx ? labels.find((y) => series.every((s) => s[y] > 0)) : null;
    const useIdx = idx && base;
    draw(holder.querySelector("canvas"), labels, series.map((s, i) => ({ label: entries[i].name, borderColor: colors[i], backgroundColor: colors[i],
      data: labels.map((y) => (s[y] == null ? null : useIdx ? +(100 * s[y] / s[base]).toFixed(1) : s[y])) })),
      useIdx ? `${m.axis}, ${base} = 100` : m.axis, { unit: useIdx ? "" : m.unit, raw: useIdx ? series : null, zero: m.kind === "rate" });
    const missing = entries.filter((e, i) => !years(series[i]).length).map((e) => e.name);
    holder.querySelector(".hist-note").textContent = [
      useIdx ? `The two places differ a lot in size, so each line is shown with ${base} = 100; hover to see the numbers.` : "",
      m.col === "Meetings by year" ? "Meetings dated by their recordings' titles (undated ones are left out; the current year is partial)." : "",
      m.col === "Poverty by year" && entries.length === 2 ? "Places in different countries use different measures." : "",
      missing.length ? `No ${m.name.toLowerCase()} by year for ${missing.join(" and ")}.` : ""].filter(Boolean).join(" ");
  }

  window.SiteHistory = { MEASURES, parse, linked, renderTrends, renderPlaces };
})();
