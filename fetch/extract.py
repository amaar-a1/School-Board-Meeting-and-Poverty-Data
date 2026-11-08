# Temporary: Philippines. HDX small-area poverty estimates and population projections (all resources), OpenSTAT poverty
# folder list, and the COD administrative boundaries (admin3: cities and municipalities), simplified with mapshaper.
import io, json, os, subprocess, traceback, urllib.request, zipfile
OUT = "fetch/out/ph3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for pid in ("philippines-small-area-poverty-estimates", "philippines-population-projection-2020-2025-admin3"):
    try:
        p = json.loads(get(f"https://data.humdata.org/api/3/action/package_show?id={pid}"))["result"]
        log.write(f"{pid}: {p.get('dataset_date')} {p.get('notes','')[:300]}\n")
        for r in p["resources"]:
            log.write(f"  res {r['name']} {r.get('format')} {r['url'][:150]}\n")
            if (r.get("format") or "").lower() in ("xlsx", "xls", "csv"):
                b = get(r["url"]); open(f"{OUT}/{pid[:20]}_{r['name']}"[:200], "wb").write(b); log.write(f"  saved {len(b)}\n")
    except Exception: log.write(traceback.format_exc()[-500:])
log.flush()
for name, u in {"openstat_1F.json": "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1F", "openstat_3D.json": "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/3D"}.items():
    try: open(f"{OUT}/{name}", "wb").write(get(u)); log.write(f"ok {name}\n")
    except Exception as e: log.write(f"ERR {name} {e}\n")
try:
    z = zipfile.ZipFile(io.BytesIO(get("https://data.humdata.org/dataset/caf116df-f984-4deb-85ca-41b349d3f313/resource/0120c30e-ba8b-487d-83f5-a664eddd3a8e/download", 1800)))
    log.write(f"cod {z.namelist()}\n")
    a3 = [n for n in z.namelist() if "adm3" in n.lower() and n.endswith(("json", "geojson"))]
    if a3:
        open("/tmp/adm3.geojson", "wb").write(z.read(a3[0]))
        subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
        r = subprocess.run(["mapshaper", "/tmp/adm3.geojson", "-simplify", "2%", "keep-shapes", "-o", f"{OUT}/ph_adm3.json", "format=geojson", "precision=0.0005"], capture_output=True, text=True)
        log.write(f"mapshaper {r.returncode} {r.stderr[-400:]}\n")
except Exception: log.write(traceback.format_exc()[-500:])
log.close()
