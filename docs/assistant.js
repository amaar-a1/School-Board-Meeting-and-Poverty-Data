// "Ask about the data": a question box that answers from the site's own data in the browser.
// It recognizes common kinds of questions (a district's figures, top/bottom lists, counts,
// averages, state comparisons, state rules, sources) rather than being a general AI.
(function () {
  const $ = (id) => document.getElementById(id);
  const POV = "Percentage of Children Ages 5-17 in Poverty", MEET = "Available Board Meetings";
  // Canadian boards use low income for ages 0-17 (a different measure; never mixed with US rows).
  const CA_POV = "Percentage of Children Ages 0-17 in Low Income";
  const METRICS = {
    poverty: { col: POV, caCol: CA_POV, ukCol: "Percentage of Children Under 16 in Low Income", label: "child poverty rate", caLabel: "child low-income rate (ages 0–17)", fmt: (v) => `${v.toFixed(1)}%` },
    meetings: { col: MEET, label: "available board meetings", fmt: (v) => v.toLocaleString() },
    enrollment: { col: "Enrollment", label: "enrollment", fmt: (v) => `${v.toLocaleString()} students` },
    children: { col: "Children Ages 5-17", caCol: "Children Ages 0-17", ukCol: "Children Under 16", label: "children ages 5–17", caLabel: "children ages 0–17", fmt: (v) => v.toLocaleString() }
  };
  // The Nordic countries and the Netherlands share one layout (r._eu is the country's name).
  const EU_POV = "Percentage of Children in Low Income";
  const EU_RE = /\b(norw\w*|swed\w*|finn?\w*|denmark|danish|netherlands|dutch|holland|german\w*|iceland\w*|new zealand|islands?|island countries)\b/i;
  const EU_OF = (q) => { const m = (q.match(EU_RE) || [])[1]; if (!m) return null; const w = m.toLowerCase();
    return w.startsWith("norw") ? "Norway" : w.startsWith("swed") ? "Sweden" : w.startsWith("fin") ? "Finland" : /^(denmark|danish)$/.test(w) ? "Denmark" : w.startsWith("german") ? "Germany" : w.startsWith("iceland") ? "Iceland" : w === "new zealand" ? "New Zealand" : w.startsWith("island") ? "Island countries and territories" : "Netherlands"; };
  const val = (r, m) => num(r[r._eu ? (m.col === POV ? r._pov : m.col === "Children Ages 5-17" ? r._kids : m.col) : r._ca && m.caCol ? m.caCol : r._uk && m.ukCol ? m.ukCol : r._ie && m.col === POV ? "Poverty rate (region, all ages)" : r._fr && m.col === POV ? "Unemployment rate (stand-in for poverty)" : m.col]);
  const UK_POV = "Percentage of Children Under 16 in Low Income";
  const povOf = (r) => num(r[r._eu ? r._pov : r._ca ? CA_POV : r._uk ? UK_POV : r._ie ? "Poverty rate (region, all ages)" : r._fr ? "Unemployment rate (stand-in for poverty)" : POV]);
  const EXAMPLES = [
    "What is the poverty rate in Austin ISD?",
    "Which districts in Ohio have the most meetings?",
    "Highest child poverty in Texas",
    "How many rural districts in Iowa have meetings?",
    "Compare California and Florida",
    "Does Oregon require recording board meetings?",
    "Highest child low income in Ontario",
    "Where does the data come from?"
  ];

  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const num = (v) => {
    const s = String(v ?? "").trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  };
  const plural = (n, word) => `${n.toLocaleString()} ${n === 1 ? word : word + "s"}`;

  // ---- data -------------------------------------------------------------------------------
  let all = [], states = {};   // all rows (states, territories, Canada); place key -> full name
  // Place keys: US state codes ("OH") and Canadian provinces ("CA:ON").
  // Other countries' places: "CA:ON", "UK:S" (each data set's groups); US states by code.
  const inPlace = (r, key) => (key.includes(":") ? r._country === key.split(":")[0] && r._group === states[key] : r.State === key);
  function data() {
    if (all.length || !window.SiteData) return all.length > 0;
    const { datasets, config } = window.SiteData;
    states = { ...config.perState.names };
    datasets.forEach((ds) => {
      if (ds.country && ds.groups) Object.entries(ds.groups.names).forEach(([k, n]) => { states[`${ds.country}:${k}`] = n; });
      ds.rows.forEach((r) => all.push({ ...r, _ca: ds.country === "CA", _uk: ds.country === "UK", _country: ds.country,
        _group: ds.groups ? r[ds.groups.column] : "", _place: r.State || r.Territory || r.Province || r.Nation || r.Region || (ds.simple ? ds.name : ""),
        _terr: !ds.country && !r.State, _fr: ds.country === "FR", _ie: ds.country === "IE", _eu: ds.simple ? ds.name : "", _pov: ds.simple ? ds.simple.pov : "", _kids: ds.simple ? ds.simple.children : "" }));
    });
    return true;
  }

  // ---- understanding the question -----------------------------------------------------------
  const GENERIC = new Set(["school", "schools", "district", "districts", "public", "independent", "isd", "cisd", "unified",
    "consolidated", "community", "unit", "the", "of", "city", "county", "department", "education", "local", "elementary"]);
  const words = (s) => s.toLowerCase().replace(/[^a-z0-9 ]/g, " ").split(/\s+/).filter(Boolean);
  // Distinctive name words, without generic words and codes like "R-XII" or "No. 5".
  const core = (name) => words(name.replace(/independent school district/i, "isd"))
    .filter((w) => !GENERIC.has(w) && !/^(\d+|[ivxlc]+|[a-z]|no)$/.test(w));

  // States named in the question: full names (any case), or two-letter codes typed in capitals.
  function findStates(q) {
    const found = [];
    let rest = q.toLowerCase();
    Object.entries(states).sort((a, b) => b[1].length - a[1].length).forEach(([abbr, name]) => {
      const re = new RegExp(`\\b${name.toLowerCase()}\\b`);
      if (re.test(rest)) { found.push(abbr); rest = rest.replace(re, " "); }
    });
    (q.match(/\b[A-Z]{2}\b/g) || []).forEach((code) => { if (states[code] && !found.includes(code)) found.push(code); });
    return found;
  }

  const LOCALES = ["Urban", "Suburban", "Town", "Rural"];
  const findLocale = (q) => LOCALES.find((l) => new RegExp(`\\b${l.toLowerCase()}\\b`).test(q.toLowerCase()));

  function findMetric(q) {
    const s = q.toLowerCase();
    if (/meeting|recorded|video|livestream/.test(s)) return "meetings";
    if (/poverty|poor|low.income|unemploy/.test(s)) return "poverty";
    if (/enrol|students|pupils|largest|biggest|smallest|size/.test(s)) return "enrollment";
    if (/children|kids|population/.test(s)) return "children";
    return null;
  }

  // Districts whose distinctive name words all appear in the question.
  function findDistricts(q, inStates) {
    const qw = new Set(words(q));
    let best = [], bestLen = 0;
    all.forEach((r) => {
      if (inStates.length && !inStates.some((k) => inPlace(r, k))) return;
      const c = core(r.District);
      if (!c.length || !c.every((w) => qw.has(w))) return;
      const len = c.join(" ").length;
      if (len > bestLen) { best = [r]; bestLen = len; } else if (len === bestLen) best.push(r);
    });
    // Ties: prefer names whose other words ("ISD", "public schools"...) are also in the question.
    const q2 = new Set(words(q.replace(/independent school district/i, "isd")));
    const overlap = (r) => words(r.District.replace(/independent school district/i, "isd")).filter((w) => q2.has(w)).length;
    const top = Math.max(0, ...best.map(overlap));
    return best.filter((r) => overlap(r) === top);
  }

  // ---- answers --------------------------------------------------------------------------------
  function scopeRows(stateList, q) {
    let rows = all;
    let label = "the United States";
    if (stateList.length === 1) { rows = all.filter((r) => inPlace(r, stateList[0])); label = states[stateList[0]]; }
    else if (/canad/i.test(q)) { rows = all.filter((r) => r._ca); label = "Canada"; }
    else if (/territor/i.test(q)) { rows = all.filter((r) => r._terr); label = "the U.S. territories"; }
    else if (/saint.pierre|miquelon/i.test(q)) { rows = all.filter((r) => r._fr); label = "Saint-Pierre-et-Miquelon"; }
    else if (/\b(uk|united kingdom|britain|british)\b/i.test(q)) { rows = all.filter((r) => r._uk); label = "the United Kingdom"; }
    else if (/\b(ireland|irish|etbs?)\b/i.test(q) && !/northern ireland/i.test(q)) { rows = all.filter((r) => r._ie); label = "Ireland"; }
    else if (EU_OF(q) && !/virgin|mariana|samoa|guam|puerto/i.test(q)) { const c = EU_OF(q); rows = all.filter((r) => r._eu === c); label = c === "Netherlands" ? "the Netherlands" : c === "Island countries and territories" ? "island countries and territories" : c; }
    else if (/\bnordic|scandinavi/i.test(q)) { rows = all.filter((r) => r._eu && r._eu !== "Netherlands"); label = "the Nordic countries"; }
    else rows = all.filter((r) => !r._terr && !r._ca && !r._fr && !r._uk && !r._ie && !r._eu);
    const unit = rows.length && rows.every((r) => r._eu === "Island countries and territories") ? "places" : rows.length && rows.every((r) => r._eu === "New Zealand") ? "areas" : rows.length && rows.every((r) => r._eu === "Germany") ? "districts" : rows.length && rows.every((r) => r._eu) ? "municipalities" : rows.length && rows.every((r) => r._ca || r._ie) ? "boards" : rows.length && rows.every((r) => r._uk) ? "councils" : "districts";
    const locale = findLocale(q);
    if (locale && unit === "districts") { rows = rows.filter((r) => r.Locale === locale); label = `${locale.toLowerCase()} districts in ${label}`; }
    else label = `${unit} in ${label}`;
    return { rows, label };
  }

  function boardCard(r) {
    const pov = povOf(r), meet = num(r[MEET]);
    return `<div class="ask-card"><strong>${esc(r.District)}, ${esc(r.Province)}</strong><ul>` +
      `<li>${esc(r["Board type"])} board</li>` +
      `<li>Children ages 0–17 in low income: ${isNaN(pov) ? "not available" : pov.toFixed(1) + "%"}` +
      (num(r["Children Ages 0-17"]) > 0 ? ` (${num(r["Children Ages 0-17 in Low Income"]).toLocaleString()} of ${num(r["Children Ages 0-17"]).toLocaleString()} children)` : "") + `</li>` +
      `<li>Board meetings found on YouTube: ${isNaN(meet) ? 0 : meet.toLocaleString()}</li>` +
      (num(r.Enrollment) > 0 ? `<li>Enrollment: ${num(r.Enrollment).toLocaleString()} (${esc(r["Enrollment year"])}${r["Enrollment note"] ? `; ${esc(r["Enrollment note"])}` : ""})</li>` : "") +
      (r.Locale ? `<li>Locale (estimated): ${esc(r.Locale)}</li>` : "") + `</ul>` +
      `<p class="ask-note">${esc(r["How poverty was calculated"] || "")}. Canada's low-income measure (LIM-AT, 2021 Census) isn't the same as the US child poverty rate.</p></div>`;
  }

  function districtCard(r) {
    if (r._ca) return boardCard(r);
    if (r._ie) {
      return `<div class="ask-card"><strong>${esc(r.District)}, Ireland</strong><ul>` +
        `<li>Poverty rate (all ages, its region): ${esc(r["Poverty rate (region, all ages)"] || "–")}</li>` +
        `<li>Unemployment (Census 2022): ${esc(r["Unemployment rate (Census 2022)"] || "–")}</li>` +
        `<li>Children 5–17: ${num(r["Children Ages 5-17"]).toLocaleString()}</li>` +
        `<li>Board meetings found: ${num(r[MEET]) || 0}</li>` + (r.Locale ? `<li>Locale (estimated): ${esc(r.Locale)}</li>` : "") + `</ul>` +
        `<p class="ask-note">${esc(r["Poverty note"] || "")}.</p></div>`;
    }
    if (r._eu) {
      const p = num(r[r._pov]), m = num(r[MEET]), e = num(r.Enrollment), isl = !!r["Poverty measure"];
      return `<div class="ask-card"><strong>${esc(r.District)}${isl ? "" : `, ${esc(r._eu)}`}</strong><ul>` +
        `<li>${isl ? esc(r["Poverty measure"] || "Poverty") : r["Poverty note"] ? "Low income (see note)" : "Children in low income"}: ${isNaN(p) ? "not published" : p.toFixed(1) + "%"}${num(r.Children) > 0 && !r["Poverty note"] ? ` (of ${num(r.Children).toLocaleString()} children)` : ""}</li>` +
        (r["Poverty note"] ? `<li>${esc(r["Poverty note"])}</li>` : "") +
        `<li>Meetings found: ${isNaN(m) ? 0 : m.toLocaleString()}</li>` +
        `<li>Pupils: ${isNaN(e) ? "not reported" : `${e.toLocaleString()}${r["Enrollment year"] ? ` (${esc(r["Enrollment year"])})` : ""}`}</li>` +
        (r.Locale ? `<li>Locale (estimated): ${esc(r.Locale)}</li>` : "") + `</ul>` +
        `<p class="ask-note">${isl ? "One education ministry or department runs its schools. This figure isn't comparable with other places' rates." : r._eu === "New Zealand" ? "A Stats NZ child poverty area (each school has its own board)." : r._eu === "Germany" ? "A district (Kreis or kreisfreie Stadt), which runs local schools' buildings and staff other than teachers." : `A municipality, which runs local schools. ${esc(r._eu)}'s child low-income measure isn't the same as the US or other countries' rates.`}</p></div>`;
    }
    const pov = num(r[POV]), meet = num(r[MEET]), enr = num(r.Enrollment);
    const note = r.Notes || r["Poverty figures"] || "";
    return `<div class="ask-card"><strong>${esc(r.District)}${r.County ? `, ${esc(r.County)}` : ""}${r._place ? `, ${esc(r._place)}` : ""}</strong><ul>` +
      `<li>Child poverty (ages 5–17): ${isNaN(pov) ? "not available" : pov.toFixed(1) + "%"}` +
      (!(num(r["Children Ages 5-17"]) > 0) ? "" : ` (${num(r["Children Ages 5-17 in Poverty"]).toLocaleString()} of ${num(r["Children Ages 5-17"]).toLocaleString()} children)`) + `</li>` +
      `<li>Available board meetings: ${isNaN(meet) ? "0 (no school board)" : meet.toLocaleString()}</li>` +
      (num(r["Other Board Meetings"]) > 0 ? `<li>Board meetings from other sources: ${num(r["Other Board Meetings"]).toLocaleString()} (${esc(r["Other meetings source"])})</li>` : "") +
      `<li>Enrollment: ${isNaN(enr) ? "not reported" : enr.toLocaleString()}</li>` +
      (r.Locale ? `<li>Locale: ${esc(r.Locale)}</li>` : "") +
      (r["School board"] ? `<li>School board: ${esc(r["School board"])}</li>` : "") +
      `</ul>${note ? `<p class="ask-note">${esc(note)}</p>` : ""}</div>`;
  }

  function ranking(q, metricKey, stateList) {
    const m = METRICS[metricKey];
    const low = /\b(lowest|least|fewest|smallest|bottom|minimum)\b/i.test(q);
    const n = Math.min(Number((q.match(/\b(?:top|bottom|first)?\s*(\d{1,2})\b/i) || [])[1]) || 5, 20);
    const { rows, label } = scopeRows(stateList, q);
    const list = rows.filter((r) => !isNaN(val(r, m)))
      .sort((a, b) => (val(a, m) - val(b, m)) * (low ? 1 : -1)).slice(0, n);
    const mLabel = rows.length && rows[0]._eu === "Island countries and territories" && metricKey === "poverty" ? "poverty rate (or stand-in)" : rows.length && rows[0]._eu && metricKey === "poverty" ? "child low-income rate (each country's own measure)" : rows.length && rows[0]._ca && m.caLabel ? m.caLabel : rows.length && rows[0]._ie && metricKey === "poverty" ? "poverty rate (all ages, each board's region)" : rows.length && rows[0]._fr && metricKey === "poverty" ? "unemployment rate (stand-in for poverty)" : m.label;
    if (!list.length) return `I couldn't find any ${esc(label)} with a ${mLabel}${rows.some((r) => r._ca) && metricKey === "enrollment" ? " (a few Canadian boards have no enrollment figure)" : ""}.`;
    if (metricKey === "meetings" && !low && num(list[0][MEET]) === 0) return `None of the ${esc(label)} have available board meetings on record.`;
    return `<p>${low ? "Lowest" : "Highest"} ${mLabel} among ${esc(label)}:</p><ol>` +
      list.map((r) => `<li>${esc(r.District)}${stateList.length === 1 ? "" : `, ${esc(r._place)}`}: ${m.fmt(val(r, m))}</li>`).join("") + "</ol>";
  }

  function summary(rows) {
    const pov = rows.map(povOf).filter((v) => !isNaN(v));
    const withM = rows.filter((r) => num(r[MEET]) > 0);
    const avg = (a) => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : NaN);
    const avgPov = (rs) => avg(rs.map(povOf).filter((v) => !isNaN(v)));
    return { n: rows.length, ca: rows.length > 0 && rows.every((r) => r._ca), avgPov: avg(pov), withM: withM.length, povWith: avgPov(withM),
      povWithout: avgPov(rows.filter((r) => !(num(r[MEET]) > 0))), meetings: rows.reduce((t, r) => t + (num(r[MEET]) || 0), 0) };
  }
  const pct = (v) => (isNaN(v) ? "–" : `${v.toFixed(1)}%`);

  function overview(stateList, q) {
    const { rows, label } = scopeRows(stateList, q);
    if (!rows.length) return `I couldn't find any ${esc(label)}.`;
    const s = summary(rows);
    return `<p>${esc(label[0].toUpperCase() + label.slice(1))} (${s.n.toLocaleString()}):</p><ul>` +
      `<li>Average ${s.ca ? "child low-income rate (ages 0–17)" : "child poverty rate"}: ${pct(s.avgPov)}</li>` +
      `<li>With available board meetings: ${s.withM.toLocaleString()} (${pct((100 * s.withM) / s.n)}), ${s.meetings.toLocaleString()} meetings in all</li>` +
      `<li>Average ${s.ca ? "child low income" : "child poverty"}, with meetings vs. without: ${pct(s.povWith)} vs. ${pct(s.povWithout)}</li></ul>` +
      (s.ca ? `<p class="ask-note">Canada's low-income measure (LIM-AT, 2021 Census) isn't the same as the US child poverty rate.</p>` : "");
  }

  function count(q, stateList) {
    const { rows, label } = scopeRows(stateList, q);
    const unit = label.startsWith("boards") ? "board" : "district";
    if (/meeting/i.test(q)) {
      const w = rows.filter((r) => num(r[MEET]) > 0).length;
      const without = /\b(no|without|none|zero)\b/i.test(q);
      return without
        ? `${plural(rows.length - w, unit)} of ${rows.length.toLocaleString()} ${esc(label)} have no available board meetings on record.`
        : `${plural(w, unit)} of ${rows.length.toLocaleString()} ${esc(label)} have available board meetings (${pct((100 * w) / Math.max(rows.length, 1))}).`;
    }
    const over = q.match(/(?:over|above|more than|at least)\s*(\d+)\s*%/i), under = q.match(/(?:under|below|less than)\s*(\d+)\s*%/i);
    if (over || under) {
      const t = Number((over || under)[1]);
      const k = rows.filter((r) => (over ? povOf(r) >= t : povOf(r) < t)).length;
      return `${plural(k, unit)} of ${rows.length.toLocaleString()} ${esc(label)} have a child poverty rate ${over ? "of" : "under"} ${t}%${over ? " or more" : ""}.`;
    }
    return `There are ${rows.length.toLocaleString()} ${esc(rows.length === 1 ? label.replace(/^(\w+ )?(districts|boards)/, (m) => m.replace(/s$/, "")) : label)}.`;
  }

  function compare(stateList) {
    const rows = stateList.map((a) => [states[a], summary(all.filter((r) => inPlace(r, a)))]);
    const mixed = rows.some(([, s]) => s.ca) && rows.some(([, s]) => !s.ca);
    return `<table class="ask-table"><thead><tr><th></th>${rows.map(([n]) => `<th>${esc(n)}</th>`).join("")}</tr></thead><tbody>` +
      `<tr><td>Districts or boards</td>${rows.map(([, s]) => `<td>${s.n.toLocaleString()}</td>`).join("")}</tr>` +
      `<tr><td>Average child poverty${mixed ? " (US) / low income (Canada)" : rows[0][1].ca ? " (low income, 0–17)" : ""}</td>${rows.map(([, s]) => `<td>${pct(s.avgPov)}</td>`).join("")}</tr>` +
      `<tr><td>With available meetings</td>${rows.map(([, s]) => `<td>${s.withM.toLocaleString()} (${pct((100 * s.withM) / s.n)})</td>`).join("")}</tr>` +
      `<tr><td>Total meetings</td>${rows.map(([, s]) => `<td>${s.meetings.toLocaleString()}</td>`).join("")}</tr>` +
      `<tr><td>Poverty with / without meetings</td>${rows.map(([, s]) => `<td>${pct(s.povWith)} / ${pct(s.povWithout)}</td>`).join("")}</tr>` +
      `</tbody></table>` + (mixed ? `<p class="ask-note">Canada's low-income rate (ages 0–17, LIM-AT) and the US child poverty rate (ages 5–17, SAIPE) are different measures, so compare them with care.</p>` : "");
  }

  function rules(stateList) {
    const r = window.STATE_RULES;
    if (!r) return "The state rules aren't loaded.";
    const ca = r.canada;
    if (ca && (stateList.some((a) => a.startsWith("CA:")) || /canad|province/i.test(lastQ))) {
      const provs = stateList.filter((a) => a.startsWith("CA:")).map((a) => states[a]);
      const laws = ca.laws.filter((x) => !provs.length || provs.includes(x.state));
      return `<p>No Canadian province requires school boards to record or stream their meetings (checked ${esc(ca.checked)}).</p>` +
        (laws.length ? `<ul>${laws.map((x) => `<li><strong>${esc(x.state)}</strong> (${esc(x.covers)}): ${esc(x.rule)}</li>`).join("")}</ul>`
          : `<p>${esc(provs.join(", "))}: meetings must be open to the public and minutes kept; nothing on recording or streaming was found.</p>`);
    }
    if (stateList.length) {
      return stateList.filter((a) => !a.startsWith("CA:")).map((a) => {
        const name = states[a], laws = r.laws.filter((x) => x.state === name), bill = r.proposed.find((x) => x.state === name);
        return `<p><strong>${esc(name)}</strong>: ` + (laws.length
          ? laws.map((x) => `${esc(x.covers)} — ${esc(x.rule)}`).join(" ")
          : `no requirement to record or stream school board meetings was found (checked ${esc(r.checked)}); usually only written minutes are required.`) +
          (bill ? ` <em>Proposed:</em> ${esc(bill.note)}` : "") + "</p>";
      }).join("");
    }
    const names = [...new Set(r.laws.map((x) => x.state))];
    return `<p>${names.length} states have a rule on recording or streaming school board meetings (checked ${esc(r.checked)}): ${names.map(esc).join(", ")}. ` +
      `Texas and Oregon set their cutoff by enrollment; Louisiana and Montana by population. Ask about a state for details, or open the State rules tab.</p>`;
  }

  function help(q) {
    const s = q.toLowerCase();
    if (/update|refresh|how often|current|latest/.test(s)) {
      return "Board meeting counts for the US and every state are refreshed daily from CivicSearch. Child poverty (Census 2024 estimates), enrollment and locale (NCES 2023), the map's borders (Census 2024), the territories' figures and the state rules are fixed snapshots, noted on the Sources tab.";
    }
    if (/locale|urban|rural|suburb/.test(s)) {
      return "Locale is the NCES type of area a district serves: Urban (a city), Suburban, Town or Rural. The “Urban & suburban” sections count both urban and suburban districts.";
    }
    if (/meeting/.test(s) && /what|mean|count/.test(s)) {
      return "“Available board meetings” is how many of a district's board meetings CivicSearch has recordings or transcripts for. Districts it doesn't cover show 0. For the territories, the counts are board meetings posted on the boards' own YouTube channels.";
    }
    if (/canad|province/.test(s)) {
      return "Canada's figures come from Statistics Canada (children 0–17 in low income, LIM-AT, 2021 Census, worked out for each board from census subdivisions inside its border), provincial board border files, and board meetings counted on each board's YouTube channel. They're kept separate from the US figures. Sources are on the Sources tab when Canada is picked.";
    }
    return "The data comes from the Census Bureau (child poverty, SAIPE 2024; 2020 Census for most territories), NCES (enrollment and locale), CivicSearch (board meeting counts), and state laws for the rules. Canada's comes from Statistics Canada, provincial border files and the boards' YouTube channels. Every source is linked on the Sources tab.";
  }

  let lastQ = "";
  function answer(q) {
    lastQ = q;
    if (!data()) return "The data is still loading — try again in a moment.";
    if (/saint.pierre|miquelon/i.test(q)) {   // before district names: a South Dakota district is called "Pierre"
      const r = all.find((x) => x._fr);
      if (r) return districtCard(r).replace("Child poverty (ages 5–17): not available", `Unemployment (stand-in for poverty): ${esc(r["Unemployment rate (stand-in for poverty)"] || "–")} (2015 est.)`) + (r["Meetings note"] ? `<p class="ask-note">${esc(r["Meetings note"])}</p>` : "");
    }
    const stateList = findStates(q);
    const s = q.toLowerCase();
    if (/\b(sources?|come from|data from|updated?|refresh(ed)?|how often|locale|mean|means|meaning)\b/.test(s) && !findDistricts(q, stateList).length) return help(q);
    if (/\b(rule|law|require|required|legal|mandate)\b/.test(s)) return rules(stateList);
    if (stateList.length >= 2 || (/\bcompare|\bvs\.?\b|versus/.test(s) && stateList.length >= 2)) return compare(stateList.slice(0, 4));
    const metric = findMetric(q);
    if (/\bhow many\b|\bnumber of\b|\bcount\b/.test(s)) return count(q, stateList);
    if (/\b(highest|most|top|largest|biggest|lowest|least|fewest|smallest|bottom|rank)\b/.test(s)) return ranking(q, metric || "poverty", stateList);
    const matches = findDistricts(q, stateList);
    if (matches.length === 1) return districtCard(matches[0]);
    if (matches.length > 1) {
      const top = matches.sort((a, b) => (num(b.Enrollment) || 0) - (num(a.Enrollment) || 0));
      return `<p>I found ${matches.length} districts with that name. Add the state to narrow it down, e.g. “${esc(top[0].District.split(" ")[0])} in ${esc(states[top[0]._place] || top[0]._place)}”.</p>` +
        top.slice(0, 3).map(districtCard).join("") + (matches.length > 3 ? `<p class="ask-note">…and ${matches.length - 3} more.</p>` : "");
    }
    if (/\baverage|\bmean|\btypical|\boverall|\bsummary|\bhow (is|are|does)/.test(s) || stateList.length === 1 || /territor/.test(s)) return overview(stateList, q);
    return `I'm not sure how to answer that. I can look up a district's figures, list the highest or lowest districts, count districts, ` +
      `compare states, and explain the state rules and sources. Try one of these:` +
      `<div class="ask-chips">${EXAMPLES.slice(0, 4).map((e) => `<button type="button" class="ask-chip">${esc(e)}</button>`).join("")}</div>`;
  }

  // ---- panel ------------------------------------------------------------------------------------
  function add(html, who) {
    const d = document.createElement("div");
    d.className = `ask-msg ask-${who}`;
    if (who === "user") d.textContent = html; else d.innerHTML = html;
    $("ask-log").appendChild(d);
    $("ask-log").scrollTop = $("ask-log").scrollHeight;
  }

  function ask(q) {
    q = q.trim();
    if (!q) return;
    add(q, "user");
    add(answer(q), "bot");
    $("ask-input").value = "";
  }

  function build() {
    const wrap = document.createElement("div");
    wrap.innerHTML = `
      <button id="ask-open" class="ask-open" type="button" aria-expanded="false" aria-controls="ask-panel">Ask about the data</button>
      <section id="ask-panel" class="ask-panel" role="dialog" aria-label="Ask about the data" hidden>
        <div class="ask-head"><strong>Ask about the data</strong><button id="ask-close" type="button" aria-label="Close">×</button></div>
        <div id="ask-log" class="ask-log" aria-live="polite">
          <div class="ask-msg ask-bot"><p>Ask about any school district, state or territory, or Canadian board or province, on this site. I answer from the site's own data.</p>
            <div class="ask-chips">${EXAMPLES.map((e) => `<button type="button" class="ask-chip">${esc(e)}</button>`).join("")}</div></div>
        </div>
        <form id="ask-form" class="ask-form"><input id="ask-input" type="text" placeholder="Type a question…" aria-label="Your question" autocomplete="off"><button type="submit">Ask</button></form>
        <p class="ask-foot">Not an AI chatbot: it recognizes common questions and answers from the data on this site.</p>
      </section>`;
    document.body.appendChild(wrap);
    const toggle = (open) => {
      $("ask-panel").hidden = !open;
      $("ask-open").setAttribute("aria-expanded", String(open));
      $("ask-open").hidden = open;
      if (open) $("ask-input").focus();
    };
    $("ask-open").addEventListener("click", () => toggle(true));
    $("ask-close").addEventListener("click", () => toggle(false));
    $("ask-form").addEventListener("submit", (e) => { e.preventDefault(); ask($("ask-input").value); });
    $("ask-log").addEventListener("click", (e) => { if (e.target.classList.contains("ask-chip")) ask(e.target.textContent); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("ask-panel").hidden) toggle(false); });
  }

  window.SiteAssistant = { answer };
  build();
})();
