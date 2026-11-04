# Temporary: Ireland local authority boundaries (to split Dublin between its two ETBs).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/ie2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "*/*"}
log, found = [], []
def get(url):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d = r.read(); log.append(f"ok {len(d)} {url[:150]}"); return d
    except Exception as e:
        log.append(f"FAIL {url[:150]}: {e}"); return None
for q in ["Local Authorities Ireland boundaries", "Administrative Areas OSi National Statutory Boundaries", "Local Authority Boundaries Ireland 2019", "Ireland local authorities Esri Ireland"]:
    d = get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": q, "f": "json", "num": 25}))
    for r in (json.loads(d).get("results", []) if d else []):
        if r["type"] == "Feature Service" and r.get("url"):
            found.append((r["title"], r["owner"], r["url"]))
json.dump(found, open(f"{OUT}/search.json", "w"), indent=1)
for t, o, u in found:
    if re.search(r"local authorit|administrative area", t, re.I) and not re.search(r"electoral|LEA|ward|town", t, re.I):
        meta = get(u.rstrip("/") + "?f=json")
        layers = json.loads(meta).get("layers", []) if meta else []
        for l in layers[:4]:
            q = get(f"{u.rstrip('/')}/{l['id']}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultRecordCount=100&maxAllowableOffset=0.002")
            if q and 25 <= len(json.loads(q).get("features", [])) <= 40:
                open(f"{OUT}/ie_la.geojson", "wb").write(q); log.append(f"picked {t} ({o}) layer {l['name']}")
                break
        if os.path.exists(f"{OUT}/ie_la.geojson"):
            break
open(f"{OUT}/log.txt", "w").write("\n".join(log))
