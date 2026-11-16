import os, json, urllib.request, urllib.parse, re
OUT = "fetch/out/disc6"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(name, url, keep=80000000, show=600, data=None):
    try:
        h = dict(UA); 
        if data is not None: h["Content-Type"] = "application/json"; data = json.dumps(data).encode()
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r: b = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(b[:keep])
        log.write(f"== {name} OK {len(b)} {url}\n{b[:show].decode('utf-8','replace')}\n\n"); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n\n"); return None
def walk(tag, base, path, depth):
    b = get(None, base + path, show=0)
    if not b: return
    try: items = json.loads(b)
    except Exception: return
    if isinstance(items, dict):
        log.write(f"{tag} TABLE {path}: {items.get('title')} | " + " | ".join(f"{v['code']}[{len(v['values'])}]: {v['valueTexts'][:4]}" for v in items.get("variables", [])) + "\n"); return
    for it in items:
        log.write(f"{tag} {'  '*depth}{path}/{it['id']} [{it['type']}] {it['text']}\n")
        if depth < 3 and it["type"] == "l": walk(tag, base, f"{path}/{it['id']}", depth + 1)
        elif it["type"] == "t" and re.search(r"municipal|administrative unit|novad|pašvald|local government|school|pupil|student|learner|general education|needy|poverty|benefit|population by", it["text"], re.I):
            walk(tag, base, f"{path}/{it['id']}", depth + 1)
# GISCO LAU 2024 for the Baltics
try:
    b = get(None, "https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_2024_4326.geojson", show=0)
    d = json.loads(b)
    for cc in ("EE", "LV", "LT"):
        f = [x for x in d["features"] if x["properties"].get("CNTR_CODE") == cc]
        json.dump({"type": "FeatureCollection", "features": f}, open(f"{OUT}/lau_{cc}.geojson", "w"))
        log.write(f"LAU {cc} {len(f)} {f[0]['properties'] if f else ''}\n")
except Exception as e: log.write(f"LAU ERR {e}\n")
walk("EE", "https://andmed.stat.ee/api/v1/en/stat", "/haridus", 0)
walk("EE", "https://andmed.stat.ee/api/v1/en/stat", "/sotsiaalne-kaitse", 0)
walk("EE", "https://andmed.stat.ee/api/v1/en/stat", "/rahvastik", 0)
walk("LV", "https://data.stat.gov.lv/api/v1/en/OSP_PUB", "/VES", 0)
walk("LV", "https://data.stat.gov.lv/api/v1/en/OSP_PUB", "/IZG", 0)
walk("LV", "https://data.stat.gov.lv/api/v1/en/OSP_PUB", "/FIN", 0)
walk("LV", "https://data.stat.gov.lv/api/v1/en/OSP_PUB", "/POP", 0)
get("lt_rs.xml", "https://osp-rs.stat.gov.lt/rest_xml/dataflow/", show=800)
get("ee_ehis.json", "https://enda.ehis.ee/avaandmed/rest/oppeasutused/-/-/-/-/-/-/-/-/-/0/0/JSON", show=1500)
get("ee_hs.html", "https://www.haridussilm.ee/ee/tasemeharidus/opetajad-ja-oppijad", show=300)
# Netherlands DUO: pupils per school site and the school address list (with denomination)
for n, u in [("nl_po_brin6.csv", "https://onderwijsdata.duo.nl/dataset/cf80e90d-ed19-4a10-a138-00c5c345cb5e/resource/9278ae97-4014-49f4-91fc-8cc255c2595d/download/brin6_totaal.csv"),
             ("nl_vo_01.csv", "https://beheer-ggm-ckan-prd.apps.prd.duo.rijksapps.nl/dataset/173cbf21-1567-464a-bccd-518cd7a46bd0/resource/d49219cc-2f36-4c2d-8007-b385ba44ec8d/download/01voins.csv"),
             ("nl_vo_02.csv", "https://beheer-ggm-ckan-prd.apps.prd.duo.rijksapps.nl/dataset/19c81dcb-a7c5-4410-8122-145f0996d082/resource/a0ca4915-9aae-4826-bf5b-6825ce95b8b4/download/02voins.csv")]:
    get(n, u, show=700)
for q in ["adressen vestigingen", "vestigingen denominatie", "leerlingen so vso per vestiging"]:
    b = get(None, "https://onderwijsdata.duo.nl/api/3/action/package_search?q=" + urllib.parse.quote(q) + "&rows=8", show=0)
    try:
        for p in json.loads(b)["result"]["results"]:
            log.write(f"DUO[{q}] {p['title']}: " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:4]) + "\n")
    except Exception as e: log.write(f"duo {q} ERR {e}\n")
# Wallonia-Brussels: Opendatasoft search
for q in ["fase", "implantation", "population scolaire", "réseau", "élèves"]:
    b = get(None, "https://www.odwb.be/api/explore/v2.1/catalog/datasets?where=" + urllib.parse.quote(f'search("{q}")') + "&limit=60&select=dataset_id", show=0)
    try:
        ids = [x["dataset_id"] for x in json.loads(b)["results"]]
        for ds in ids:
            if re.match(r"^\d", ds) or "ores" in ds or "cadastre" in ds: continue
            m = get(None, f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{ds}", show=0)
            mm = json.loads(m); log.write(f"ODWB[{q}] {ds}: {mm['metas']['default'].get('title')} | {[f['name'] for f in mm.get('fields', [])][:14]}\n")
    except Exception as e: log.write(f"odwb {q} ERR {e}\n")
