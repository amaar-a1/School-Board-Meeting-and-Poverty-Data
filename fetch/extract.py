# Temporary: UK/Ireland part 4: ONS district-to-county lookup; CSO table catalogue (Ireland).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/ukie4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "*/*"}
log = []
def get(url, name=None):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
# ONS: Local Authority District to County (December 2024) lookup in England
d = get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": "Local Authority District to County December 2024 Lookup in England", "f": "json", "num": 10}))
for r in (json.loads(d)["results"] if d else []):
    if r["owner"] == "ONSGeography_data" and r["type"] == "Feature Service" and "2024" in r["title"]:
        q = get(r["url"].rstrip("/") + "/0/query?where=1%3D1&outFields=*&f=json&resultRecordCount=2000")
        if q:
            open(f"{OUT}/ons_lad_cty_2024.json", "wb").write(q); log.append("lookup: " + r["title"])
        break
# Ireland: CSO PxStat catalogue, keep tables that may hold county-level unemployment or school enrolment
d = get("https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadCollection")
if d:
    j = json.loads(d)
    items = j.get("link", {}).get("item", []) if isinstance(j, dict) else []
    keep = []
    for it in items:
        lab = it.get("label", "")
        if re.search(r"(principal economic status|unemploy).*(county|administrative|local authority)|(county|administrative).*(principal economic status|unemploy)|enrol.*(county|ETB|education and training)", lab, re.I):
            keep.append((it.get("extension", {}).get("matrix"), lab, it.get("updated")))
    json.dump(keep, open(f"{OUT}/cso_tables.json", "w"), indent=1)
    log.append(f"CSO tables: {len(items)}, kept {len(keep)}")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
