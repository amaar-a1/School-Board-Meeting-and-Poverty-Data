// "Find a district" (top of every tab): search all districts (states and territories), show a card
// with the district's figures, and jump to it on the map, in the data table or in its state's view.
(function () {
  const $ = (id) => document.getElementById(id);
  const POV = "Percentage of Children Ages 5-17 in Poverty", MEET = "Available Board Meetings";
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const num = (v) => {
    const s = String(v ?? "").trim().replace(/[$,%\s]/g, "");
    return s === "" ? NaN : Number(s);
  };
  const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9 ]/g, " ").replace(/\bsaint\b/g, "st").replace(/\s+/g, " ");

  let index = [], shown = [], active = -1, names = {};

  function init() {
    const { datasets, config } = window.SiteData;
    names = config.perState.names;
    datasets.forEach((ds) => ds.rows.forEach((r) => {
      const place = r.State ? names[r.State] : r.Territory;
      index.push({ row: r, terr: !r.State, label: [r.County, r.State || r.Territory].filter(Boolean).join(", "),
        text: norm(`${r.District} ${r.County || ""} ${r.State || ""} ${place || ""}`), size: num(r.Enrollment) || 0 });
    }));
    const box = $("find-input");
    box.addEventListener("input", show);
    box.addEventListener("keydown", (e) => {
      const items = [...$("find-results").querySelectorAll("li[data-i]")];
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
      } else if (e.key === "Escape") hide();
    });
    $("find-results").addEventListener("mousedown", (e) => {
      const li = e.target.closest("li[data-i]");
      if (li) { e.preventDefault(); choose(Number(li.dataset.i)); }
    });
    box.addEventListener("blur", () => setTimeout(hide, 150));
    $("find-card").addEventListener("click", action);
    $("find").hidden = false;
  }

  function show() {
    const q = norm($("find-input").value).trim();
    active = -1;
    if (q.length < 2) return hide();
    const words = q.split(/\s+/);
    shown = index.filter((e) => words.every((w) => e.text.includes(w)))
      .sort((a, b) => (norm(b.row.District).startsWith(q) - norm(a.row.District).startsWith(q)) || b.size - a.size)
      .slice(0, 8);
    $("find-results").innerHTML = shown.length
      ? shown.map((e, i) => `<li role="option" data-i="${i}" aria-selected="false"><strong>${esc(e.row.District)}</strong><span>${esc(e.label)}</span></li>`).join("")
      : `<li class="map-results-none">No district found</li>`;
    $("find-results").hidden = false;
    $("find-input").setAttribute("aria-expanded", "true");
  }

  function hide() {
    $("find-results").hidden = true;
    $("find-input").setAttribute("aria-expanded", "false");
  }

  let picked = null;
  function choose(i) {
    picked = shown[i];
    if (!picked) return;
    hide();
    const r = picked.row;
    $("find-input").value = r.District;
    const pov = num(r[POV]), meet = num(r[MEET]), enr = num(r.Enrollment), kids = num(r["Children Ages 5-17"]);
    const note = r.Notes || r["Poverty figures"] || "";
    const where = picked.terr ? "the U.S. territories" : names[r.State];
    $("find-card").innerHTML =
      `<div class="find-head"><div><h2>${esc(r.District)}</h2><p class="muted">${esc(picked.label)}</p></div>` +
      `<button type="button" class="find-close" data-act="close" aria-label="Close">×</button></div>` +
      `<div class="stats compare">` +
      stat("Child poverty (ages 5–17)", isNaN(pov) ? "–" : `${pov.toFixed(1)}%`, kids > 0 ? `${num(r["Children Ages 5-17 in Poverty"]).toLocaleString()} of ${kids.toLocaleString()} children` : "") +
      stat("Available board meetings", isNaN(meet) ? "0" : meet.toLocaleString(), isNaN(meet) ? "no school board" : "") +
      stat("Enrollment", isNaN(enr) ? "–" : enr.toLocaleString(), isNaN(enr) ? "not reported" : "students") +
      stat("Locale", r.Locale || "–", "") + `</div>` +
      (note ? `<p class="note">${esc(note)}</p>` : "") +
      `<div class="find-actions"><button type="button" data-act="map">Show on map</button>` +
      `<button type="button" data-act="table">Show in data table</button>` +
      `<button type="button" data-act="state">View ${esc(where)}</button></div>`;
    $("find-card").hidden = false;
  }

  function stat(label, value, sub) {
    return `<div class="stat"><div class="label">${esc(label)}</div><div class="value">${esc(value)}</div><div class="sub">${esc(sub)}</div></div>`;
  }

  function action(e) {
    const act = e.target.dataset.act;
    if (!act || !picked) return;
    const sd = window.SiteData, r = picked.row;
    if (act === "close") { $("find-card").hidden = true; return; }
    sd.select(picked.terr ? "territories" : r.State);
    if (act === "map") {
      sd.setView("map");
      history.replaceState(null, "", "#map");
      if (window.SiteMap) window.SiteMap.focus(r["District ID"]);
      $("map").scrollIntoView({ behavior: "smooth", block: "center" });
    } else if (act === "table") {
      sd.setView("overview");
      history.replaceState(null, "", location.pathname + location.search);
      if (window.SiteFilters && window.SiteFilters.active() && !window.SiteFilters.test(r)) $("f-clear").click();
      $("search").value = r.District;
      $("search").dispatchEvent(new Event("input"));
      $("table-section").scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
      sd.setView("overview");
      history.replaceState(null, "", location.pathname + location.search);
    }
  }

  const wait = setInterval(() => { if (window.SiteData) { clearInterval(wait); init(); } }, 200);
})();
