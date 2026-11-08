# Temporary: Philippines. PSA city and municipal poverty estimates (2021 SAE) and municipal borders (PSGC, GitHub).
import json, os, re, urllib.parse, urllib.request
OUT = "fetch/out/ph1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    h = get("https://psa.gov.ph/statistics/poverty-sae/stat-tables").decode("utf-8", "ignore"); open(f"{OUT}/psa_tables.html", "w").write(h)
    links = sorted(set(re.findall(r'href="([^"]+\.xlsx?)"', h))); log.write("links " + json.dumps(links) + "\n")
    for l in links:
        u = urllib.parse.urljoin("https://psa.gov.ph/", l)
        try:
            b = get(u); open(f"{OUT}/{os.path.basename(urllib.parse.unquote(u))}", "wb").write(b); log.write(f"ok {u} {len(b)}\n")
        except Exception as e: log.write(f"ERR {u} {str(e)[:120]}\n")
except Exception as e: log.write(f"ERR psa {str(e)[:200]}\n")
log.flush()
# Borders: faeldon/philippines-json-maps (PSGC 2023), municipalities and cities, low resolution.
try:
    api = json.loads(get("https://api.github.com/repos/faeldon/philippines-json-maps/git/trees/master?recursive=1"))
    paths = [t["path"] for t in api["tree"] if t["path"].startswith("2023/geojson/") and "lowres" in t["path"]]
    log.write(f"tree {len(paths)} {paths[:8]}\n")
    json.dump(paths, open(f"{OUT}/tree.json", "w"))
except Exception as e: log.write(f"ERR tree {str(e)[:200]}\n")
log.close()
