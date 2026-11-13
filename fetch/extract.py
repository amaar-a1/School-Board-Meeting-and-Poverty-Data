# Temporary: Philippine school enrollment by school or municipality on HDX and other open catalogues.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/ph_enr_alt1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for q in ["philippines schools enrollment", "philippines deped schools", "philippines education facilities", "philippines learners"]:
    try:
        d = json.loads(get("https://data.humdata.org/api/3/action/package_search?rows=10&q=" + urllib.parse.quote(q)))
        for p in d["result"]["results"]:
            log.write(f"HDX | {p['name']} | {p.get('title')} | {p.get('organization',{}).get('title')} | {p.get('metadata_modified','')[:10]}\n")
            for r in p.get("resources", [])[:4]: log.write(f"      {r.get('format')} | {r.get('name','')[:70]} | {r.get('size')} | {r['url'][:160]}\n")
    except Exception as e: log.write(f"ERR hdx {q} {e}\n")
for u in ["https://api.github.com/repos/OSMPH/deped_schools_db/contents", "https://api.github.com/search/repositories?q=deped+enrollment+schools&per_page=10"]:
    try:
        d = json.loads(get(u))
        items = d if isinstance(d, list) else d.get("items", [])
        for x in items[:15]: log.write(f"GH | {x.get('full_name') or x.get('path')} | {x.get('description') or x.get('size')} | {x.get('pushed_at') or x.get('download_url')}\n")
    except Exception as e: log.write(f"ERR gh {u} {e}\n")
log.close()
