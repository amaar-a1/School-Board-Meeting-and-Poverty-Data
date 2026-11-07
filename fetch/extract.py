# Temporary: French primary-school pupils by school (rentrée 2025), overseas départements' commune borders,
# Ecuador's population by canton (2022 census) and its school register (AMIE).
import json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/fr_ec3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except urllib.error.HTTPError as e:
            body = e.read()[:400]; err = Exception(f"HTTP {e.code}: {body!r}"); time.sleep(5)
        except Exception as e:
            err = e; time.sleep(10)
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-900:]}\n\n")
    log.flush()
def save(name, u, t=900):
    b = get(u, t); open(f"{OUT}/{name}", "wb").write(b); return f"{len(b)} bytes; head {b[:300]!r}"
base = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-ecoles-effectifs-nb_classes/exports/csv?"
step("Pupils by school, rentrée 2025", lambda: save("fr_ecoles_2025.csv", base + urllib.parse.urlencode(
    {"select": "code_commune_insee,secteur,nombre_total_eleves", "where": "rentree_scolaire = date'2025'", "delimiter": ";"})))
step("Pupils by school, rentrée 2025 (text year)", lambda: save("fr_ecoles_2025b.csv", base + urllib.parse.urlencode(
    {"select": "code_commune_insee,secteur,nombre_total_eleves", "refine": "rentree_scolaire:2025", "delimiter": ";"})))
for code, slug in (("971", "guadeloupe"), ("972", "martinique"), ("973", "guyane"), ("974", "la-reunion"), ("976", "mayotte")):
    step(f"Communes {code}", lambda code=code, slug=slug: save(f"fr_communes_{code}.geojson",
         f"https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements/{code}-{slug}/communes-{code}-{slug}.geojson"))
def ckan(q):
    d = json.loads(get("https://www.datosabiertos.gob.ec/api/3/action/package_search?rows=6&q=" + urllib.parse.quote(q), 120))
    out = []
    for x in d["result"]["results"]:
        out.append(f"* {x['title']} ({(x.get('organization') or {}).get('title')})")
        for r in x.get("resources", [])[:10]: out.append(f"    - {r.get('name')} [{r.get('format')}] {r.get('url')}")
    return "\n".join(out)
for q in ("AMIE estudiantes", "registro administrativo educación instituciones educativas", "población cantón censo 2022", "pobreza NBI cantonal 2022"):
    step(f"datosabiertos.gob.ec: {q}", lambda q=q: ckan(q))
log.close()
