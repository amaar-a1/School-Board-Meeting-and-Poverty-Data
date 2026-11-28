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
    set("map-detail", s.key === "ALL" ? "region" : "place");
    set("map-metric", s.metric);
    location.hash = "map";
    window.scrollTo({ top: 0, behavior: calm ? "auto" : "smooth" });
  }

  function show(ds) {
    load().then(() => {
      const box = $("map-preview");
      if (!box) return;
      const next = slidesFor(ds);
      const sig = next.map((s) => s.src).join(",");
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
      $("map-preview-updated").textContent = list.updated ? `Map as of ${new Date(list.updated + "T12:00:00").toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })}` : "";
      paint(); tick();
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
