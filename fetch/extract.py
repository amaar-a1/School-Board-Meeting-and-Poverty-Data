# Temporary: Saint-Pierre-et-Miquelon outline (Natural Earth) and Territorial Council session minutes.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/spm2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            data = r.read()
        log.append(f"ok {len(data)} {url}"); return data
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
d = get("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_map_units.geojson")
if d:
    fc = json.loads(d)
    keep = [f for f in fc["features"] if f["properties"].get("ADM0_A3") == "SPM" or f["properties"].get("GU_A3") == "SPM" or "Pierre" in str(f["properties"].get("NAME", ""))]
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"NAME": k["properties"].get("NAME")}, "geometry": k["geometry"]} for k in keep]}, open(f"{OUT}/spm_outline.geojson", "w"))
    log.append(f"outline features: {len(keep)}")
# Territorial Council: minutes (PV) of sessions, from the collectivity's WordPress media library
pvs = []
for page in range(1, 11):
    q = get(f"https://www.spm-ct975.fr/wp-json/wp/v2/media?search=PV&per_page=100&page={page}&_fields=id,date,title,source_url")
    if not q:
        break
    items = json.loads(q)
    if not items:
        break
    pvs += [{"date": i["date"], "title": i["title"]["rendered"], "url": i["source_url"]} for i in items]
json.dump(pvs, open(f"{OUT}/ct_pv_media.json", "w"), indent=1, ensure_ascii=False)
h = get("https://www.spm-ct975.fr/")
if h:
    open(f"{OUT}/ct_home.html", "wb").write(h)
    for path in sorted(set(re.findall(rb'href="(https://www\.spm-ct975\.fr/[^"]*(?:seance|deliber|conseil|proces|pv)[^"]*)"', h, re.I)))[:8]:
        p = get(path.decode())
        if p:
            open(f"{OUT}/ct_{re.sub(r'\W+', '_', path.decode())[-60:]}.html", "wb").write(p)
open(f"{OUT}/log.txt", "w").write("\n".join(log))
