# Temporary: find France's and Ecuador's data (poverty, population, pupils, borders) for two new countries.
import json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/fr_ec1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300, hdr=None):
    err = None
    for a in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(5)
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-700:]}\n\n")
    log.flush()
def save(name, u, t=600, hdr=None):
    b = get(u, t, hdr); open(f"{OUT}/{name}", "wb").write(b); return f"{len(b)} bytes; head {b[:300]!r}"

# --- France ---
def melodi_catalog():
    b = get("https://api.insee.fr/melodi/catalog/all", hdr={"Accept": "application/json"})
    d = json.loads(b)
    keep = [x for x in d if re.search(r"FILOSOFI|POPULATION|POP_LEG", json.dumps(x.get("identifier", "")) + json.dumps(x.get("title", "")), re.I)]
    json.dump(keep, open(f"{OUT}/melodi_catalog_subset.json", "w"), ensure_ascii=False)
    return f"{len(d)} datasets; matching: " + "; ".join(f"{x.get('identifier')} | {json.dumps(x.get('title'), ensure_ascii=False)[:120]}" for x in keep[:40])
step("INSEE Melodi catalog", melodi_catalog)
step("Melodi FILOSOFI_CC sample", lambda: save("melodi_filosofi_cc_sample.json", "https://api.insee.fr/melodi/data/DS_FILOSOFI_CC?GEO=COM-75056&maxResult=200", hdr={"Accept": "application/json"}))
def datagouv(q):
    d = json.loads(get("https://www.data.gouv.fr/api/1/datasets/?page_size=8&q=" + urllib.parse.quote(q)))
    out = []
    for x in d.get("data", []):
        out.append(f"* {x['title']} ({x.get('organization', {}) and x['organization'].get('name')})")
        for r in x.get("resources", [])[:8]: out.append(f"    - {r.get('title')} [{r.get('format')}, {r.get('filesize')}] {r.get('url')}")
    return "\n".join(out)
for q in ("filosofi 2021 communes taux de pauvreté", "populations légales communes 2022", "contours communes simplifiés geojson"):
    step(f"data.gouv: {q}", lambda q=q: datagouv(q))
step("Écoles effectifs (sample)", lambda: save("fr_ecoles_effectifs_sample.json",
     "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ecoles-effectifs-nb_classes/records?limit=3&order_by=rentree_scolaire%20desc"))
step("france-geojson communes (simplified)", lambda: save("fr_communes_simplifiee.geojson",
     "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/communes-version-simplifiee.geojson"))
step("france-geojson départements (simplified)", lambda: save("fr_departements_simplifiee.geojson",
     "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"))

# --- Ecuador ---
def hdx(q):
    d = json.loads(get("https://data.humdata.org/api/3/action/package_search?rows=8&q=" + urllib.parse.quote(q)))
    out = []
    for x in d["result"]["results"]:
        out.append(f"* {x['title']} ({x.get('organization', {}).get('title')})")
        for r in x.get("resources", [])[:8]: out.append(f"    - {r.get('name')} [{r.get('format')}] {r.get('url')}")
    return "\n".join(out)
for q in ("ecuador poverty canton", "ecuador pobreza cantonal censo 2022", "ecuador population canton 2022"):
    step(f"HDX: {q}", lambda q=q: hdx(q))
def inec():
    out = []
    for u in ("https://www.ecuadorencifras.gob.ec/censo-de-poblacion-y-vivienda/", "https://www.censoecuador.gob.ec/resultados-censo/",
              "https://www.ecuadorencifras.gob.ec/pobreza-por-necesidades-basicas-insatisfechas/"):
        try:
            t = get(u, 60).decode("utf-8", "replace")
            links = sorted(set(re.findall(r'href="([^"]+\.(?:xlsx?|zip|csv))"', t, re.I)))
            out.append(f"{u}: {len(t)} chars; files: {links[:60]}")
        except Exception as e:
            out.append(f"{u}: {e}")
    return "\n".join(out)
step("INEC pages", inec)
step("geoBoundaries ECU ADM2", lambda: save("gb_ECU_ADM2.geojson",
     "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ECU/ADM2/geoBoundaries-ECU-ADM2_simplified.geojson"))
step("geoBoundaries ECU ADM1", lambda: save("gb_ECU_ADM1.geojson",
     "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ECU/ADM1/geoBoundaries-ECU-ADM1_simplified.geojson"))
log.close()
