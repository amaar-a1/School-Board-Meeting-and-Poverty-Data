# Temporary: Philippines. Border repo file list (faeldon/philippines-json-maps, latest), PSA OpenSTAT poverty tables by
# region/province (metadata and 2021 data), and the HDX COD administrative boundaries' resource list.
import json, os, urllib.request
OUT = "fetch/out/ph4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None, t=300):
    req = urllib.request.Request(u, headers={**UA, **({"Content-Type": "application/json"} if data else {})}, data=data)
    with urllib.request.urlopen(req, timeout=t) as r: return r.read()
try:
    root = json.loads(get("https://api.github.com/repos/faeldon/philippines-json-maps/git/trees/master"))
    sha = next(t["sha"] for t in root["tree"] if t["path"] == "latest")
    tree = json.loads(get(f"https://api.github.com/repos/faeldon/philippines-json-maps/git/trees/{sha}?recursive=1"))
    paths = [t["path"] for t in tree["tree"]]
    json.dump(paths, open(f"{OUT}/latest_tree.json", "w")); log.write(f"tree {len(paths)} {paths[:30]}\n")
except Exception as e: log.write(f"ERR tree {str(e)[:200]}\n")
for tid in ("0023C3DP020.px", "0013C3DP010.px"):
    try:
        u = f"https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/3D/{tid}"
        meta = json.loads(get(u)); json.dump(meta, open(f"{OUT}/{tid}_meta.json", "w"))
        q = {"query": [], "response": {"format": "json-stat2"}}
        open(f"{OUT}/{tid}_data.json", "wb").write(get(u, json.dumps(q).encode())); log.write(f"ok {tid}\n")
    except Exception as e: log.write(f"ERR {tid} {str(e)[:200]}\n")
try:
    open(f"{OUT}/openstat_1F_FY.json", "wb").write(get("https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1F/FY")); log.write("ok 1F/FY\n")
except Exception as e: log.write(f"ERR 1F/FY {e}\n")
log.close()
