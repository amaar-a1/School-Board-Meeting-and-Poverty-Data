// "Statistics" view: is poverty linked to whether a place posts any meetings, comparing places of the same size?
// For each country: a logistic regression of "has any meetings" on the place's poverty rank in its country (0 to 1)
// and the log of its size (population, or enrollment where there's no population), plus Spearman's rank correlation
// between poverty and the meeting count. Then all countries together, comparing places only with others in their own
// country (a fixed effect for each country), with standard errors clustered by country.
// Computed in the browser from the loaded data, so it follows every data update.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const RANK = "Poverty rank in country";
  const SIZE_COLS = ["Population", "Enrollment", "Children Ages 5-17", "Children Ages 5-17 (2021 Census)"];
  const MIN_N = 15, MIN_GROUP = 3;
  let cache = {};

  const num = (v) => { const n = Number(String(v ?? "").replace(/[,%\s]/g, "")); return String(v ?? "").trim() === "" ? NaN : n; };

  // Standard normal CDF (Abramowitz and Stegun 7.1.26 via erf).
  function phi(z) {
    const t = 1 / (1 + 0.3275911 * Math.abs(z) / Math.SQRT2);
    const e = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z / 2);
    return z >= 0 ? (1 + e) / 2 : (1 - e) / 2;
  }
  const pTwo = (z) => Math.max(0, Math.min(1, 2 * (1 - phi(Math.abs(z)))));

  function invert(A) {
    const n = A.length, M = A.map((r, i) => [...r, ...r.map((_, j) => (i === j ? 1 : 0))]);
    for (let c = 0; c < n; c++) {
      let p = c;
      for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
      if (Math.abs(M[p][c]) < 1e-12) return null;
      [M[c], M[p]] = [M[p], M[c]];
      const d = M[c][c];
      for (let j = 0; j < 2 * n; j++) M[c][j] /= d;
      for (let r = 0; r < n; r++) if (r !== c && M[r][c]) { const f = M[r][c]; for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j]; }
    }
    return M.map((r) => r.slice(n));
  }

  // Logistic regression by Newton-Raphson. X: rows of sparse [index, value] pairs; p: number of parameters.
  // Returns coefficients with ordinary standard errors and, given cluster labels, cluster-robust ones.
  function logit(X, y, p, clusters) {
    let b = new Array(p).fill(0);
    let H = null;
    for (let it = 0; it < 30; it++) {
      const g = new Array(p).fill(0), h = Array.from({ length: p }, () => new Array(p).fill(0));
      X.forEach((x, i) => {
        let eta = 0; x.forEach(([j, v]) => { eta += b[j] * v; });
        const mu = 1 / (1 + Math.exp(-eta)), w = Math.max(mu * (1 - mu), 1e-10);
        x.forEach(([j, v]) => { g[j] += (y[i] - mu) * v; x.forEach(([k, u]) => { h[j][k] += w * v * u; }); });
      });
      H = invert(h);
      if (!H) return null;
      const step = H.map((r) => r.reduce((s, v, k) => s + v * g[k], 0));
      b = b.map((v, j) => v + step[j]);
      if (Math.max(...step.map(Math.abs)) < 1e-8) break;
    }
    if (b.some((v) => !isFinite(v) || Math.abs(v) > 30)) return null;   // separation: no finite estimate
    const se = H.map((r, j) => Math.sqrt(r[j]));
    let cse = null;
    if (clusters) {
      const u = new Map();
      X.forEach((x, i) => {
        let eta = 0; x.forEach(([j, v]) => { eta += b[j] * v; });
        const r = y[i] - 1 / (1 + Math.exp(-eta));
        const s = u.get(clusters[i]) || new Array(p).fill(0);
        x.forEach(([j, v]) => { s[j] += r * v; });
        u.set(clusters[i], s);
      });
      const G = u.size, meat = Array.from({ length: p }, () => new Array(p).fill(0));
      u.forEach((s) => { for (let j = 0; j < p; j++) if (s[j]) for (let k = 0; k < p; k++) meat[j][k] += s[j] * s[k]; });
      const HM = H.map((r) => meat[0].map((_, k) => r.reduce((t, v, m) => t + v * meat[m][k], 0)));
      cse = HM.map((r, j) => Math.sqrt(Math.max(0, r.reduce((t, v, m) => t + v * H[m][j], 0) * G / (G - 1))));
    }
    return { b, se, cse };
  }

  function ranks(a) {
    const idx = a.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]), out = new Array(a.length);
    for (let i = 0; i < idx.length;) {
      let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
      for (let k = i; k <= j; k++) out[idx[k][1]] = (i + j) / 2;
      i = j + 1;
    }
    return out;
  }
  function spearman(a, b) {
    const n = a.length; if (n < 4) return null;
    const ra = ranks(a), rb = ranks(b), ma = (n - 1) / 2;
    let sxy = 0, sxx = 0, syy = 0;
    for (let i = 0; i < n; i++) { sxy += (ra[i] - ma) * (rb[i] - ma); sxx += (ra[i] - ma) ** 2; syy += (rb[i] - ma) ** 2; }
    if (!sxx || !syy) return null;
    const r = sxy / Math.sqrt(sxx * syy);
    return { r, p: pTwo(Math.atanh(Math.max(-0.999999, Math.min(0.999999, r))) * Math.sqrt(n - 3)) };
  }

  const sizeOf = (r) => { for (const c of SIZE_COLS) { const v = num(r[c]); if (v > 0) return v; } return NaN; };

  // One country's places: poverty rank (0 to 1; estimated ranks left out), any meetings (0/1), meeting count, log size.
  function placesOf(d, boardsOnly, S) {
    const by = (d.compare || S.cfg.compare).by;
    const out = [];
    d.rows.forEach((r) => {
      const rank = num(r[RANK]);
      if (isNaN(rank) || r._rankEst) return;
      const m = S.meetOf(r, by);
      if (isNaN(m)) return;
      const has = m > 0 && (!boardsOnly || r["Meeting body"] === S.BOARD);
      const size = sizeOf(r);
      out.push({ rank: rank / 100, any: has ? 1 : 0, count: boardsOnly && !has ? 0 : m, ls: size > 0 ? Math.log(size) : NaN });
    });
    return out;
  }

  function analyse(boardsOnly) {
    const S = window.SiteData;
    const rows = [], pooled = [];
    S.datasets.filter((d) => !d.state && d.country !== "FR").forEach((d) => {
      const all = placesOf(d, boardsOnly, S);
      const pl = all.filter((x) => isFinite(x.ls));
      const k = pl.reduce((t, x) => t + x.any, 0);
      const row = { name: d.name, key: S.keyOf(d), n: all.length, nSized: pl.length, k, share: pl.length ? k / pl.length : NaN };
      const varies = new Set(pl.map((x) => x.rank)).size > 2;
      if (pl.length < MIN_N || k < MIN_GROUP || pl.length - k < MIN_GROUP || !varies) {
        row.skip = !varies && pl.length >= MIN_N ? "one poverty figure for the whole country" : !k ? "no meetings found" : pl.length - k < MIN_GROUP ? "nearly every place has meetings" : "too few places with meetings";
        rows.push(row); return;
      }
      const sp = spearman(pl.map((x) => x.rank), pl.map((x) => x.count));
      const mls = pl.reduce((t, x) => t + x.ls, 0) / pl.length, sls = Math.sqrt(pl.reduce((t, x) => t + (x.ls - mls) ** 2, 0) / pl.length) || 1;
      const fit = logit(pl.map((x) => [[0, 1], [1, x.rank], [2, (x.ls - mls) / sls]]), pl.map((x) => x.any), 3);
      if (!fit) { row.skip = "no stable estimate"; rows.push(row); return; }
      Object.assign(row, { rho: sp && sp.r, rhoP: sp && sp.p, b: fit.b[1], se: fit.se[1], p: pTwo(fit.b[1] / fit.se[1]), size: Math.exp(fit.b[2]) });
      rows.push(row);
      pl.forEach((x) => pooled.push({ ...x, c: d.name, lz: (x.ls - mls) / sls }));
    });
    const tested = rows.filter((r) => !r.skip);
    tested.forEach((r) => { r.bonf = r.p < 0.05 / tested.length; });
    // Pooled: a fixed effect for each country (the first is the baseline), poverty rank, size within the country.
    const names = [...new Set(pooled.map((x) => x.c))], ci = new Map(names.map((c, i) => [c, i]));
    const P = names.length + 2;
    const fit = pooled.length ? logit(pooled.map((x) => [[0, 1], ...(ci.get(x.c) ? [[ci.get(x.c) + 2, 1]] : []), [1, x.rank], [2, x.lz]]), pooled.map((x) => x.any), P, pooled.map((x) => x.c)) : null;
    const pool = fit ? { n: pooled.length, countries: names.length, b: fit.b[1], se: fit.cse[1], p: pTwo(fit.b[1] / fit.cse[1]), size: Math.exp(fit.b[2]) } : null;
    return { rows, pool, tested: tested.length };
  }

  const f2 = (v) => (isFinite(v) ? v.toFixed(2) : "–");
  const pFmt = (p) => (!isFinite(p) ? "–" : p < 0.001 ? "< 0.001" : p.toFixed(3));
  const orText = (b) => (isFinite(b) ? Math.exp(b).toFixed(2) : "–");
  function verdict(r) {
    if (r.skip) return `Not tested (${r.skip})`;
    if (r.p >= 0.05) return "No clear link";
    return `${Math.exp(r.b) < 1 ? "Poorer places post less" : "Poorer places post more"}${r.bonf ? "" : " (weak)"}`;
  }

  // Forest plot cell: the odds ratio and its 95% range on a log scale from 1/100 to 100.
  function forest(r) {
    if (r.skip) return "";
    const lo = Math.exp(r.b - 1.96 * r.se), hi = Math.exp(r.b + 1.96 * r.se), or = Math.exp(r.b);
    const x = (v) => Math.max(0, Math.min(100, 50 + 25 * Math.log10(v)));
    const col = r.p < 0.05 ? (or < 1 ? "var(--forest-less, #c0392b)" : "var(--forest-more, #2471a3)") : "var(--muted, #888)";
    return `<svg class="forest" viewBox="0 0 100 12" preserveAspectRatio="none" aria-hidden="true"><line x1="50" y1="0" x2="50" y2="12" stroke="currentColor" stroke-opacity="0.35" stroke-width="0.6"/>` +
      `<line x1="${x(lo)}" y1="6" x2="${x(hi)}" y2="6" stroke="${col}" stroke-width="1.4"/><circle cx="${x(or)}" cy="6" r="2.4" fill="${col}"/></svg>`;
  }

  function render(current) {
    const S = window.SiteData;
    if (!S) return;
    const boardsOnly = !!($("stats-boards") && $("stats-boards").checked);
    const key = boardsOnly ? "b" : "a";
    const res = cache[key] || (cache[key] = analyse(boardsOnly));
    const here = current && !current.combined ? current.name : "";
    const t = $("stats-table");
    t.tHead.innerHTML = "<tr><th>Country</th><th class=\"num\">Places</th><th class=\"num\">With meetings</th><th class=\"num\" title=\"Spearman's rank correlation between poverty and the number of meetings\">Rank corr.</th>" +
      "<th class=\"num\" title=\"Odds of posting any meetings, the poorest place vs. the richest, at the same size\">Odds ratio</th><th class=\"num\">95% range</th><th class=\"forest-head\"><span>¹⁄₁₀₀</span><span>1</span><span>100</span></th><th class=\"num\">p</th><th>Result</th></tr>";
    const body = t.tBodies[0];
    body.innerHTML = "";
    const order = (r) => (r.skip ? 2 : r.p < 0.05 ? 0 : 1);
    [...res.rows].sort((a, b) => order(a) - order(b) || (a.p ?? 1) - (b.p ?? 1) || b.n - a.n).forEach((r) => {
      const tr = body.insertRow();
      if (r.name === here) tr.className = "stats-here";
      const cells = [r.name, r.n.toLocaleString(), isFinite(r.share) ? `${(100 * r.share).toFixed(1)}%` : "–", r.skip ? "–" : f2(r.rho),
        r.skip ? "–" : orText(r.b), r.skip ? "–" : `${orText(r.b - 1.96 * r.se)}–${orText(r.b + 1.96 * r.se)}`, null, r.skip ? "–" : pFmt(r.p), verdict(r)];
      cells.forEach((v, i) => {
        const td = tr.insertCell();
        if (i === 6) { td.innerHTML = forest(r); td.className = "forest-cell"; return; }
        td.textContent = v;
        if (i && i < 8) td.className = "num";
      });
    });
    const less = res.rows.filter((r) => !r.skip && r.p < 0.05 && r.b < 0), more = res.rows.filter((r) => !r.skip && r.p < 0.05 && r.b > 0);
    const P = res.pool;
    $("stats-summary").innerHTML = P
      ? `<p><strong>All countries together: ${P.p < 0.05 ? (P.b < 0 ? "poorer places post meetings less often" : "poorer places post meetings more often") : "no overall link"}.</strong> ` +
        `Comparing each place only with others of the same size in its own country, the poorest place has ${orText(P.b)} times the odds of the richest of posting any meetings ` +
        `(95% range ${orText(P.b - 1.96 * P.se)}–${orText(P.b + 1.96 * P.se)}, p ${pFmt(P.p)}; ${P.n.toLocaleString()} places in ${P.countries} countries, standard errors clustered by country). ` +
        `Size matters far more: a place one standard deviation larger than average for its country has ${P.size.toFixed(1)} times the odds.</p>` +
        `<p>Country by country, ${less.length} of the ${res.tested} countries tested show poorer places posting less (${less.filter((r) => r.bonf).length} of them still after correcting for testing ${res.tested} countries), ` +
        `and ${more.length} show poorer places posting more (${more.filter((r) => r.bonf).length} after correcting).${less.length && more.length && P.p >= 0.05 ? " The links run both ways, so they cancel out overall." : ""}</p>`
      : "<p>Not enough data to test.</p>";
    $("stats-download").onclick = () => {
      const head = ["Country", "Places", "Places with a size", "With meetings (share)", "Rank correlation", "Rank correlation p", "Odds ratio, poorest vs richest", "95% low", "95% high", "p", "Holds after correction", "Result"];
      const data = res.rows.map((r) => [r.name, r.n, r.nSized, isFinite(r.share) ? r.share.toFixed(4) : "", r.skip ? "" : f2(r.rho), r.skip ? "" : pFmt(r.rhoP),
        r.skip ? "" : orText(r.b), r.skip ? "" : orText(r.b - 1.96 * r.se), r.skip ? "" : orText(r.b + 1.96 * r.se), r.skip ? "" : pFmt(r.p), r.skip ? "" : r.bonf ? "yes" : "no", verdict(r)]);
      if (P) data.push(["All countries (country fixed effects, clustered SE)", P.n, P.n, "", "", "", orText(P.b), orText(P.b - 1.96 * P.se), orText(P.b + 1.96 * P.se), pFmt(P.p), "", ""]);
      const csv = window.Papa.unparse({ fields: head, data });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
      a.download = `poverty-and-meetings-statistics${boardsOnly ? "-boards-only" : ""}.csv`;
      a.click();
      URL.revokeObjectURL(a.href);
    };
  }

  window.SiteStats = { render, analyse, reset: () => { cache = {}; } };
})();
