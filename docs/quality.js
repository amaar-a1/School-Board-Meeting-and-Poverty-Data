// Data quality labels: how solid each country's figures are, worked out from the data itself.
// Poverty: what kind of figure it is (a published rate, a modelled estimate, a stand-in, or one national rate), how
// old, and the share of places with a figure of their own. Enrollment: the share of places with a count, an estimate
// (school-age children) or nothing. Meetings: whether the meetings found are a school board's (or an equivalent body's)
// or a council's or parliament's standing in for one. Shown under each country's note, and as a table on the Sources tab.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const RANK = "Poverty rank in country";
  const YEAR = new Date().getFullYear();
  // The countries whose config has no one-line poverty measure.
  const MEASURE = {
    "United States": "Children 5–17 in poverty (Census Bureau's model-based small-area estimates, SAIPE, 2024)",
    "U.S. territories": "Children in poverty: Census estimates for Puerto Rico (2024); the 2020 Census (2019 incomes) for the other territories",
    "Canada": "Children 0–17 in low income (after-tax low-income measure, 2021 Census, 2020 incomes); reserves: the surrounding area's rate as a stand-in",
    "Saint-Pierre-et-Miquelon (France)": "Stand-in: unemployment rate (2015 estimate)",
    "United Kingdom": "Children under 16 in relative low income before housing costs (Department for Work and Pensions, 2025)",
    "Ireland": "Stand-in: the overall at-risk-of-poverty rate of the Eurostat region (all ages), 2024",
    "Islands and microstates": "Each place's own measure (mostly national rates or stand-ins; see each row)"
  };
  const num = (v) => { const s = String(v ?? "").trim(); const n = Number(s.replace(/[,%\s]/g, "")); return s === "" ? NaN : n; };

  function kindOf(name, full) {
    const measure = String(full).split(";")[0];   // the main measure (Canada's reserves' stand-in comes after a semicolon)
    if (/national rate|each place's own measure/i.test(measure)) return "National rates";
    if (/stand-in|unemployment|welfare rate|social assistance|receiving|recipients|benefit|on public assistance/i.test(measure)) return "Stand-in";
    if (/estimate|small-area|poverty map|model|SAIPE|midpoint/i.test(measure)) return "Modelled estimate";
    return "Published rate";
  }
  const yearsIn = (s) => (String(s).match(/(?<!\d)(19[89]\d|20[0-4]\d)(?!\d)/g) || []).map(Number);
  // The figure's year: the first year named, or the end of a range ("2022–2024", "2019-21").
  function yearOf(s) {
    const m = String(s).match(/(?<!\d)(19[89]\d|20[0-4]\d)(?:\s*[–-]\s*(\d{2,4}))?(?!\d)/);
    if (!m) return null;
    if (!m[2]) return Number(m[1]);
    return m[2].length === 2 ? Number(m[1].slice(0, 2) + m[2]) : Number(m[2]);
  }

  function quality(d) {
    const rows = d.rows, n = rows.length || 1;
    const measure = (d.simple && d.simple.measure) || MEASURE[d.name] || "";
    const kind = kindOf(d.name, measure);
    const year = yearOf(measure);
    const own = rows.filter((r) => String(r[RANK] ?? "") !== "" && !r._rankEst).length;
    const count = rows.filter((r) => num(r.Enrollment) > 0 && !r["Enrollment estimated"] && !/estimated/i.test(r["Enrollment year"] || "")).length;
    const est = rows.filter((r) => num(r.Enrollment) > 0 && (r["Enrollment estimated"] || /estimated/i.test(r["Enrollment year"] || ""))).length;
    const ey = {};
    rows.forEach((r) => { if (num(r.Enrollment) > 0 && !r["Enrollment estimated"]) yearsIn(r["Enrollment year"]).slice(0, 1).forEach((y) => { ey[y] = (ey[y] || 0) + 1; }); });
    const eyear = Object.entries(ey).sort((a, b) => b[1] - a[1])[0];
    const withM = rows.filter((r) => r["Meeting body"]).length, board = rows.filter((r) => r["Meeting body"] === "School board or equivalent").length;
    return { measure, kind, year, ownShare: own / n, countShare: count / n, estShare: est / n, enrollYear: eyear ? Number(eyear[0]) : null,
      meetShare: withM / n, boardShare: withM ? board / withM : NaN };
  }

  // good / fair / weak, for the colour of each label.
  function grades(q) {
    const age = q.year ? YEAR - q.year : 99;
    const pov = q.kind === "Published rate" || q.kind === "Modelled estimate" ? (age <= 4 && q.ownShare > 0.9 ? "good" : age <= 9 ? "fair" : "weak") : q.kind === "Stand-in" ? "fair" : "weak";
    const enr = q.countShare > 0.9 ? "good" : q.countShare + q.estShare > 0.9 ? "fair" : "weak";
    const meet = !q.meetShare ? "weak" : q.boardShare > 0.5 ? "good" : "fair";
    return { pov, enr, meet };
  }
  const pct = (v) => `${Math.round(100 * v)}%`;
  function texts(q) {
    const age = q.year ? `, ${q.year}` : "";
    return {
      pov: `${q.kind}${age}${q.ownShare < 0.995 ? `; ${pct(q.ownShare)} of places have their own figure` : ""}`,
      enr: q.countShare > 0.995 ? `Counted${q.enrollYear ? `, ${q.enrollYear}` : ""}` : q.countShare + q.estShare < 0.005 ? "None" :
        `${q.countShare > 0.005 ? `${pct(q.countShare)} counted${q.enrollYear ? ` (${q.enrollYear})` : ""}` : ""}${q.countShare > 0.005 && q.estShare > 0.005 ? ", " : ""}${q.estShare > 0.005 ? `${pct(q.estShare)} estimated` : ""}`,
      meet: !q.meetShare ? "None found" : `${pct(q.meetShare)} of places; ${q.boardShare > 0.995 ? "all a school board's or equivalent" : q.boardShare < 0.005 ? "all a stand-in body's (council or parliament)" : `${pct(q.boardShare)} a school board's or equivalent, the rest a stand-in's`}`
    };
  }
  const GRADE_WORD = { good: "solid", fair: "use with care", weak: "weak" };

  function chip(label, grade, text, title) {
    const s = document.createElement("span");
    s.className = `q-chip q-${grade}`;
    s.title = `${label}: ${GRADE_WORD[grade]}${title ? ` (${title})` : ""}`;
    s.innerHTML = `<i aria-hidden="true"></i><b></b>: <span></span>`;
    s.querySelector("b").textContent = label;
    s.querySelector("span").textContent = text;
    return s;
  }

  function renderFor(current, target) {
    const el = target || $("quality");
    if (!el) return;
    el.innerHTML = "";
    if (!current) { el.hidden = true; return; }
    el.hidden = false;
    if (current.combined) {
      el.innerHTML = `<span class="q-title">Data quality:</span> it differs a lot from country to country; see each country's labels, or the table on the <a href="#sources">Sources</a> tab.`;
      return;
    }
    const q = quality(current), g = grades(q), t = texts(q);
    const title = document.createElement("span"); title.className = "q-title"; title.textContent = "Data quality:";
    el.append(title, chip("Poverty", g.pov, t.pov, q.measure), chip("Enrollment", g.enr, t.enr), chip("Meetings", g.meet, t.meet));
  }

  function renderTable(datasets) {
    const t = $("quality-table");
    if (!t) return;
    t.tHead.innerHTML = "<tr><th>Country</th><th>Poverty measure</th><th>Poverty</th><th>Enrollment</th><th>Meetings</th></tr>";
    const body = t.tBodies[0];
    body.innerHTML = "";
    datasets.filter((d) => !d.state || d.state === "territories").forEach((d) => {
      const q = quality(d), g = grades(q), tx = texts(q);
      const tr = body.insertRow();
      tr.insertCell().textContent = d.name;
      tr.insertCell().textContent = q.measure;
      [["pov", tx.pov], ["enr", tx.enr], ["meet", tx.meet]].forEach(([k, v]) => {
        const td = tr.insertCell();
        td.innerHTML = `<span class="q-chip q-${g[k]}"><i aria-hidden="true"></i><span></span></span>`;
        td.querySelector("span span").textContent = v;
        td.title = GRADE_WORD[g[k]];
      });
    });
  }

  window.SiteQuality = { quality, renderFor, renderTable };
})();
