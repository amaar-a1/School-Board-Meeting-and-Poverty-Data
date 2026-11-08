# Temporary: Australia. Census 2021 General Community Profile for local government areas (LGA, 2021 ASGS) - only the
# tables needed, as CSV; LGA 2021 borders simplified with mapshaper; DSS payment demographic data (latest quarter, LGA sheet).
import csv, io, json, os, re, subprocess, traceback, urllib.request, zipfile
OUT = "fetch/out/au1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=600):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    z = zipfile.ZipFile(io.BytesIO(get("https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_LGA_for_AUS_short-header.zip")))
    names = z.namelist(); log.write(f"gcp files {len(names)}\n")
    for n in names:
        b = os.path.basename(n)
        if re.search(r"_(G01|G02|G15|G28|G29|G33|G34|G35)[AB]?_AUS_LGA\.csv$", b) or (b.endswith(".xlsx") and "Metadata" in b) or "Metadata" in b and b.endswith(".csv"):
            open(f"{OUT}/{b}", "wb").write(z.read(n)); log.write(f"saved {b}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.flush()
try:
    z = zipfile.ZipFile(io.BytesIO(get("https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026/access-and-downloads/digital-boundary-files/LGA_2021_AUST_GDA2020_SHP.zip")))
    os.makedirs("/tmp/lga", exist_ok=True); z.extractall("/tmp/lga"); log.write(f"lga {z.namelist()}\n")
    shp = [f for f in os.listdir("/tmp/lga") if f.endswith(".shp")][0]
    subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
    r = subprocess.run(["mapshaper", f"/tmp/lga/{shp}", "-filter", "'$.geometry' !== null", "-simplify", "1.5%", "keep-shapes", "-o", f"{OUT}/lga2021.json", "format=geojson", "precision=0.0005"], capture_output=True, text=True)
    log.write(f"mapshaper {r.returncode} {r.stderr[-500:]}\n")
    if not os.path.exists(f"{OUT}/lga2021.json"):
        r = subprocess.run(["mapshaper", f"/tmp/lga/{shp}", "-simplify", "1.5%", "keep-shapes", "-o", f"{OUT}/lga2021.json", "format=geojson", "precision=0.0005"], capture_output=True, text=True)
        log.write(f"mapshaper2 {r.returncode} {r.stderr[-500:]}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.flush()
try:
    p = json.loads(get("https://data.gov.au/data/api/3/action/package_show?id=dss-payment-demographic-data"))
    res = p["result"]["resources"]
    json.dump([{k: r.get(k) for k in ("name", "url", "format", "last_modified", "created")} for r in res], open(f"{OUT}/dss_resources.json", "w"), indent=0)
    xl = [r for r in res if (r.get("format") or "").lower() in ("xlsx", "xls") or r["url"].lower().endswith((".xlsx", ".xls"))]
    xl.sort(key=lambda r: r.get("created") or "", reverse=True)
    for r in xl[:2]:
        b = get(r["url"]); open(f"{OUT}/dss_{len(os.listdir(OUT))}_{os.path.basename(r['url'])[:80]}", "wb").write(b); log.write(f"dss {r['name']} {len(b)}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
