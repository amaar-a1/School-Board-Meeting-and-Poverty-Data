# Temporary: Philippines. Every province's (and NCR district's) city and municipality borders from
# faeldon/philippines-json-maps (latest, low resolution), merged and simplified with mapshaper; PSA OpenSTAT table 2a
# (poverty incidence among population by region, province and highly urbanized city: 2018, 2021, 2023).
import json, os, subprocess, time, urllib.request
OUT = "fetch/out/ph5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None, t=300):
    req = urllib.request.Request(u, headers={**UA, **({"Content-Type": "application/json"} if data else {})}, data=data)
    with urllib.request.urlopen(req, timeout=t) as r: return r.read()
paths = [p for p in json.load(open("fetch/out/ph4/latest_tree.json")) if p.startswith("geojson/provdists/lowres/municities-provdist-")]
feats = []
for p in paths:
    try:
        g = json.loads(get(f"https://raw.githubusercontent.com/faeldon/philippines-json-maps/master/latest/{p}"))
        feats += g["features"]; time.sleep(0.2)
    except Exception as e: log.write(f"ERR {p} {str(e)[:100]}\n")
log.write(f"features {len(feats)} {feats[0]['properties'] if feats else ''}\n")
json.dump({"type": "FeatureCollection", "features": feats}, open("/tmp/ph_all.json", "w"))
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
r = subprocess.run(["mapshaper", "/tmp/ph_all.json", "-simplify", "25%", "keep-shapes", "-o", f"{OUT}/ph_municities.json", "format=geojson", "precision=0.0005"], capture_output=True, text=True)
log.write(f"mapshaper {r.returncode} {r.stderr[-300:]}\n")
try:
    u = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1F/FY/0041F3DF02A.px"
    json.dump(json.loads(get(u)), open(f"{OUT}/t2a_meta.json", "w"))
    open(f"{OUT}/t2a_data.json", "wb").write(get(u, json.dumps({"query": [], "response": {"format": "json-stat2"}}).encode())); log.write("ok t2a\n")
except Exception as e: log.write(f"ERR t2a {str(e)[:200]}\n")
log.close()
