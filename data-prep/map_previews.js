// Pictures of the map for the Overview's preview (docs/img/map-preview/), taken from the site itself with a headless
// browser, so they show the latest data:
//   - the whole world, by district or municipality, coloured by each of several measures: <metric>.jpg
//   - each country's and US state's own view, by district or municipality, for a few measures: v/<key>/<metric>.jpg
// and previews.json, which lists them. Run by .github/workflows/map-previews.yml whenever docs/data changes (and by
// hand: serve docs/ on port 8765, then `node data-prep/map_previews.js`). Map tiles are left out, so the pictures
// show only the site's own colours.
//   LIBS=dir     serve the page's script libraries from a local node_modules (where the CDNs can't be reached)
//   ONLY=k,k     only these views (keys as in the site's links: ALL for the world, PE, TX, ...); the rest of
//                previews.json is kept
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const OUT = path.join(__dirname, "..", "docs", "img", "map-preview");
const BASE = process.env.BASE || "http://localhost:8765/index.html";
const WORLD = ["poverty", "meetings", "perYear", "density", "public", "locale", "enrollment", "changePop"];
const VIEW = ["poverty", "meetings", "density"];
const ONLY = process.env.ONLY ? new Set(process.env.ONLY.split(",")) : null;
const LOCAL = { "papaparse.min.js": "papaparse/papaparse.min.js", "chart.umd.min.js": "chart.js/dist/chart.umd.js", "leaflet.min.js": "leaflet/dist/leaflet.js",
  "topojson-client.min.js": "topojson-client/dist/topojson-client.min.js", "leaflet.min.css": "leaflet/dist/leaflet.css" };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const listFile = path.join(OUT, "previews.json");
  let old = {};
  try { old = JSON.parse(fs.readFileSync(listFile, "utf8")); } catch (e) { /* none yet */ }
  const list = { updated: new Date().toISOString().slice(0, 10), titles: old.titles || {}, world: old.world || [], views: old.views || {}, boxes: old.boxes || {} };
  delete list.items;
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 900, height: 760 }, deviceScaleFactor: 1 });
  await ctx.route(/basemaps\.cartocdn|tile\.openstreetmap/, (r) => r.abort());
  if (process.env.LIBS) await ctx.route(/cdnjs|jsdelivr/, (r) => { const f = LOCAL[r.request().url().split("/").pop()];
    return f ? r.fulfill({ path: path.join(process.env.LIBS, f), contentType: f.endsWith(".css") ? "text/css" : "application/javascript" }) : r.abort(); });
  const p = await ctx.newPage();
  p.on("pageerror", (e) => console.error("page error:", e.message));

  // Opens a view on the map, then takes a picture for each measure it has.
  async function shoot(key, query, metrics, dir) {
    await p.goto(`${BASE}?${query}&theme=light&metric=${metrics[0]}#map`, { waitUntil: "load" });
    await p.waitForTimeout(1200);
    await p.evaluate(() => { const d = document.getElementById("terms-gate"); if (d && d.open) d.close(); });
    await p.addStyleTag({ content: ".leaflet-control-container, .map-legend, .leaflet-control { display: none !important; }" });
    await p.waitForFunction(() => document.querySelectorAll("#map canvas").length > 0, null, { timeout: 60000 });
    await p.waitForTimeout(3000);
    await p.waitForFunction(() => !document.getElementById("map-status").textContent, null, { timeout: 90000 }).catch(() => {});
    await p.waitForTimeout(3000);   // the borders and colours finish drawing
    const got = [];
    // where the pictures are of, so the Overview can mark a region on them
    const v = await p.evaluate(() => window.SiteMap && window.SiteMap.view && window.SiteMap.view());
    if (v) list.boxes[key] = v;
    for (const m of metrics) {
      const title = await p.evaluate((m) => {
        const s = document.getElementById("map-metric"), o = [...s.options].find((x) => x.value === m && !x.disabled && !x.hidden);
        if (!o) return null;
        if (s.value !== m) { s.value = m; s.dispatchEvent(new Event("change")); }
        return o.textContent.trim();
      }, m);
      if (!title) continue;   // not a measure this view has
      await p.waitForTimeout(1500);
      fs.mkdirSync(path.join(OUT, dir), { recursive: true });
      await p.locator("#map").screenshot({ path: path.join(OUT, dir, `${m}.jpg`), type: "jpeg", quality: dir ? 62 : 78 });
      got.push(m);
      list.titles[`${key}:${m}`] = title;
    }
    console.log("map preview:", key, got.join(" "));
    return got;
  }

  if (!ONLY || ONLY.has("ALL")) list.world = await shoot("ALL", "d=ALL&at=22,10,2", WORLD, "");
  // The views: each country, and each US state
  await p.goto(BASE, { waitUntil: "load" });
  await p.waitForFunction(() => window.SiteData && window.SiteData.datasets.length > 5, null, { timeout: 60000 });
  const keys = await p.evaluate(() => {
    const SD = window.SiteData;
    const ds = SD.datasets.filter((d) => !d.combined && !d.state && d.country !== "ISLE" && d.rows.length > 1).map((d) => SD.keyOf(d));
    return ds.concat(Object.keys((SD.config.perState || {}).names || {}).filter((k) => SD.fromKey(k)));
  });
  for (const k of keys) {
    if (ONLY && !ONLY.has(k)) continue;
    const got = await shoot(k, `d=${encodeURIComponent(k)}`, VIEW, `v/${k}`);
    if (got.length) list.views[k] = got; else delete list.views[k];
  }
  fs.writeFileSync(listFile, JSON.stringify(list) + "\n");
  await b.close();
})();
