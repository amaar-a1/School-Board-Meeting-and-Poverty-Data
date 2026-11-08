# Temporary: Philippines 2020 census population by city and municipality (HDX COD population statistics).
import json, os, urllib.request
OUT = "fetch/out/ph8"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for pid in ("cod-ps-phl", "philippines-2020-census-of-population-and-housing"):
    try:
        p = json.loads(get(f"https://data.humdata.org/api/3/action/package_show?id={pid}"))["result"]
        log.write(f"{pid}: {p.get('title')} {p.get('dataset_date')}\n")
        for r in p["resources"]:
            log.write(f"  {r['name']} {r.get('format')} {r['url'][:160]}\n")
            if (r.get("format") or "").lower() in ("csv", "xlsx") and ("adm3" in r["name"].lower() or "admin3" in r["name"].lower() or "mun" in r["name"].lower()):
                b = get(r["url"]); open(f"{OUT}/{r['name'][:120]}", "wb").write(b); log.write(f"  saved {len(b)}\n")
    except Exception as e: log.write(f"ERR {pid} {str(e)[:150]}\n")
log.close()
