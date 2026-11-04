# Temporary: Nordics + Netherlands discovery: statistics tables (child low income, pupils) and municipal borders.
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
OUT = "fetch/out/nordic"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.5)
    try:
        req = urllib.request.Request(url, headers=UA, data=data)
        with urllib.request.urlopen(req, timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:160]}"); return d
    except Exception as e:
        log.append(f"FAIL {url[:160]}: {e}"); return None
def save(name, obj): json.dump(obj, open(f"{OUT}/{name}", "w"), indent=1, ensure_ascii=False)
# Norway (SSB PxWeb v0 search)
for q in ["lavinntekt barn kommune", "elever grunnskolen kommune"]:
    d = get("https://data.ssb.no/api/v0/no/table/?" + urllib.parse.urlencode({"query": q}))
    if d: save(f"no_{q.split()[0]}.json", [(t.get("id"), t.get("text"), t.get("updated")) for t in json.loads(d)][:40])
# Sweden (SCB PxWebApi v2 search)
for q in ["låg ekonomisk standard barn kommun", "elever grundskolan kommun"]:
    d = get("https://statistikdatabasen.scb.se/api/v2/tables?" + urllib.parse.urlencode({"query": q, "lang": "sv", "pageSize": 40}))
    if d: save(f"se_{q.split()[0]}.json", [(t.get("id"), t.get("label"), t.get("updated")) for t in json.loads(d).get("tables", [])])
# Finland (Statistics Finland PxWeb search; THL Sotkanet indicator list)
for q in ["pienituloisuus lapset kunta", "peruskoulu oppilaat kunta"]:
    d = get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/?" + urllib.parse.urlencode({"query": q}))
    if d: save(f"fi_{q.split()[0]}.json", [(t.get("id"), t.get("title"), t.get("path"), t.get("published")) for t in json.loads(d)][:40])
d = get("https://sotkanet.fi/rest/1.1/indicators")
if d:
    save("fi_sotkanet_lowincome.json", [(i.get("id"), i.get("title", {}).get("fi"), i.get("title", {}).get("en")) for i in json.loads(d)
                                          if re.search(r"pienituloi|low.income", json.dumps(i.get("title", {})), re.I)])
# Denmark (Statbank table list, filter)
d = get("https://api.statbank.dk/v1/tables?lang=en&format=JSON")
if d:
    save("dk_tables.json", [(t["id"], t["text"], t.get("updated")) for t in json.loads(d)
                            if re.search(r"poverty|low.income|relative poor|pupils|primary and lower secondary", t["text"], re.I)])
# Netherlands (CBS OData catalogue)
d = get("https://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$select=Identifier,Title,Modified,Period&$top=20000")
if d:
    save("nl_tables.json", [(t["Identifier"], t["Title"], t.get("Period"), t.get("Modified")) for t in json.loads(d)["value"]
                            if re.search(r"laag inkomen|armoede|kinderen in|kerncijfers wijken|leerlingen", t["Title"], re.I)])
# Municipal borders: Eurostat GISCO LAU (all EU/EFTA), keep these five countries
for year in ("2023", "2021"):
    url = f"https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_{year}_4326.geojson"
    d = get(url)
    if d:
        fc = json.loads(d)
        for cc in ("NO", "SE", "FI", "DK", "NL"):
            feats = [f for f in fc["features"] if f["properties"].get("CNTR_CODE") == cc]
            json.dump({"type": "FeatureCollection", "features": feats}, open(f"/tmp/lau_{cc}.geojson", "w"))
            log.append(f"LAU {year} {cc}: {len(feats)} {feats[0]['properties'] if feats else ''}")
        break
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
for cc in ("NO", "SE", "FI", "DK", "NL"):
    if os.path.exists(f"/tmp/lau_{cc}.geojson"):
        subprocess.run(f"mapshaper -i /tmp/lau_{cc}.geojson -simplify 3% keep-shapes -o {OUT}/lau_{cc}.geojson precision=0.0001", shell=True)
open(f"{OUT}/log.txt", "w").write("\n".join(log))
