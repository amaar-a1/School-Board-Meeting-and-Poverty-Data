// The map's preview at the top of the Overview: pictures of the map (img/map-preview/, made by
// data-prep/map_previews.js from the latest data) for the view on screen, the whole world by region or a country's
// or US state's own districts, taking turns through the measures. Clicking one opens the map on that measure.
(function () {
  const $ = (id) => document.getElementById(id);
  const DIR = "img/map-preview/";
  const calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let list = null, loading = null, timer = null, slides = [], at = 0, paused = false, showing = null;

  const load = () => loading || (loading = fetch(DIR + "previews.json").then((r) => (r.ok ? r.json() : null)).catch(() => null)
    .then((j) => { list = j; return j; }));

  // The pictures for a data set: its own, or for a region's view its country's.
  function slidesFor(ds) {
    if (!list || !ds) return [];
    const SD = window.SiteData, key = ds.combined ? "ALL" : SD.keyOf(ds);
    const of = (k, ms, dir) => (ms || []).map((m) => ({ key: k, metric: m, src: DIR + dir + m + ".jpg", title: (list.titles || {})[`${k}:${m}`] || m }));
    if (key === "ALL") return of("ALL", list.world, "");
    for (let d = ds; d; d = d.parent) {
      const k = SD.keyOf(d);
      if (list.views && list.views[k]) return of(k, list.views[k], `v/${k}/`);
    }
    const c = ds.country && SD.fromKey(ds.country);   // a region's view: its country's pictures
    const k = c ? SD.keyOf(c) : "";
    return k && list.views && list.views[k] ? of(k, list.views[k], `v/${k}/`) : [];
  }

  function paint() {
    const box = $("map-preview");
    const s = slides[at];
    if (!s) return;
    box.querySelectorAll("img").forEach((img, i) => img.classList.toggle("on", i === at));
    $("map-preview-title").textContent = s.title;
    box.querySelectorAll(".map-preview-dots button").forEach((b, i) => b.setAttribute("aria-current", i === at ? "true" : "false"));
  }
  function go(i) { at = (i + slides.length) % slides.length; paint(); }
  function tick() {
    clearInterval(timer);
    if (!calm && slides.length > 1) timer = setInterval(() => { if (!paused && !document.hidden) go(at + 1); }, 4000);
  }

  function open() {
    const s = slides[at], SD = window.SiteData;
    if (!s || !SD) return;
    const set = (id, v) => { const el = $(id); if (el && [...el.options].some((o) => o.value === v)) { el.value = v; el.dispatchEvent(new Event("change")); } };
    SD.setView("map");
    set("map-detail", "place");
    set("map-metric", s.metric);
    location.hash = "map";
    window.scrollTo({ top: 0, behavior: calm ? "auto" : "smooth" });
  }

  // A region's view shows its country's pictures, with the region outlined on them: its outline
  // (data/map/regions/<country's data file>.json) placed by where the pictures are of (previews.json's boxes, the
  // map's view when they were taken: west, south, east, north, and the size in pixels), in Web Mercator like the map.
  const regionFiles = {};
  function regionOverlay(ds, key) {
    const old = document.getElementById("map-preview-mark");
    if (old) old.remove();
    const SD = window.SiteData, box = list && list.boxes && list.boxes[key];
    if (!ds || !box || !SD || ds.combined || SD.keyOf(ds) === key) return Promise.resolve("");
    const parent = ds.parent || SD.fromKey(key);
    const file = parent && parent.file ? String(parent.file).split("/").pop().replace(/\.csv$/, "") : "";
    if (!file || !ds.rows || !ds.rows.length) return Promise.resolve("");
    const got = regionFiles[file] || (regionFiles[file] = fetch(`data/map/regions/${file}.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null));
    return got.then((d) => {
      const lines = d && (d.regions || {})[String(ds.rows[0][d.col] ?? "")];
      if (!lines) return "";
      const [w, so, e, n] = box.box, [W, H] = box.size;
      const Y = (lat) => Math.log(Math.tan(Math.PI / 4 + (Math.max(-85, Math.min(85, lat)) * Math.PI) / 360));
      const px = (x, y) => `${(((x - w) / (e - w)) * W).toFixed(1)},${(((Y(n) - Y(y)) / (Y(n) - Y(so))) * H).toFixed(1)}`;
      const path = lines.map((l) => "M" + l.map(([x, y]) => px(x, y)).join("L") + "Z").join("");
      const NS = "http://www.w3.org/2000/svg", svg = document.createElementNS(NS, "svg");
      svg.id = "map-preview-mark"; svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("preserveAspectRatio", "xMidYMid slice");
      svg.setAttribute("aria-hidden", "true");
      [["halo", 6], ["line", 3]].forEach(([cls, sw]) => {
        const el = document.createElementNS(NS, "path");
        el.setAttribute("d", path); el.setAttribute("class", `mark-${cls}`); el.setAttribute("stroke-width", sw);
        el.setAttribute("vector-effect", "non-scaling-stroke"); el.setAttribute("fill", "none"); el.setAttribute("stroke-linejoin", "round");
        svg.appendChild(el);
      });
      document.getElementById("map-preview-pics").appendChild(svg);
      return ds.name || "";
    });
  }

  function show(ds) {
    load().then(() => {
      const box = $("map-preview");
      if (!box) return;
      const next = slidesFor(ds);
      const sig = next.map((s) => s.src).join(",") + "|" + (ds && ds.name);
      if (sig === showing) return;
      showing = sig; slides = next; at = 0;
      box.hidden = !slides.length;
      clearInterval(timer);
      if (!slides.length) return;
      const pics = $("map-preview-pics");
      pics.innerHTML = "";
      slides.forEach((s, i) => {
        const img = new Image();
        img.src = s.src; img.alt = `Map: ${s.title}`; img.decoding = "async";
        if (i) img.loading = "lazy";
        pics.appendChild(img);
      });
      const dots = box.querySelector(".map-preview-dots");
      dots.innerHTML = "";
      slides.forEach((s, i) => {
        const b = document.createElement("button");
        b.type = "button"; b.title = s.title; b.setAttribute("aria-label", `Show ${s.title}`);
        b.addEventListener("click", (e) => { e.stopPropagation(); go(i); tick(); });
        dots.appendChild(b);
      });
      const asOf = list.updated ? `Map as of ${new Date(list.updated + "T12:00:00").toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })}` : "";
      $("map-preview-updated").textContent = asOf;
      paint(); tick();
      regionOverlay(ds, slides[0].key).then((name) => { if (name) $("map-preview-updated").textContent = `Outlined: ${name}` + (asOf ? ` · ${asOf}` : ""); });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const box = $("map-preview");
    if (!box) return;
    const btn = $("map-preview-open");
    btn.addEventListener("click", open);
    box.addEventListener("mouseenter", () => { paused = true; });
    box.addEventListener("mouseleave", () => { paused = false; });
    box.addEventListener("focusin", () => { paused = true; });
    box.addEventListener("focusout", () => { paused = false; });
  });

  window.SitePreview = { show };
})();
