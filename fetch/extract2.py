# Round 23: India child population by district (for an enrollment estimate; UDISE+ doesn't answer from here).
# HDX (CKAN API) search, then download the small tabular resources of the packages that look like population by age.
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/in23"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
pk = {}
for q in ["india population age district", "india subnational population statistics", "cod-ps-ind", "india census 2011 age",
          "india population 0-14 district", "india admin2 population age sex"]:
    try:
        d = json.loads(get("https://data.humdata.org/api/3/action/package_search?rows=20&q=" + urllib.parse.quote(q)))
        for p in d["result"]["results"]:
            pk[p["name"]] = p
            log.write(f"{q} | {p['name']} | {p['title']} | {[ (r['name'], r.get('format'), r.get('size')) for r in p['resources']]}\n")
    except Exception as e: log.write(f"ERR search {q}: {e}\n")
    time.sleep(2)
json.dump({k: {"title": v["title"], "notes": v.get("notes", "")[:1500], "resources": [{"name": r["name"], "url": r["url"], "format": r.get("format"), "size": r.get("size")} for r in v["resources"]]} for k, v in pk.items()},
          open(f"{OUT}/packages.json", "w"), indent=1)
n = 0
for k, v in pk.items():
    t = (v["title"] + " " + k).lower()
    if "india" not in t or not any(w in t for w in ("population", "census", "demograph")): continue
    for r in v["resources"]:
        if (r.get("format") or "").upper() not in ("CSV", "XLSX", "XLS", "ZIP") or (r.get("size") or 0) > 60e6: continue
        fn = f"{n:02d}_" + os.path.basename(urllib.parse.urlparse(r["url"]).path)[-80:]; n += 1
        try: b = get(r["url"], 300); open(f"{OUT}/{fn}", "wb").write(b); log.write(f"OK {fn} {len(b)} {r['url']}\n")
        except Exception as e: log.write(f"ERR {fn} {e} {r['url']}\n")
        time.sleep(2)
log.close()
