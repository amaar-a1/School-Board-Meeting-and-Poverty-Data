# Temporary: French primary-school pupils by school with the school's INSEE commune code (the pupils file's
# "code_commune_insee" is the postal code), from the school directory (annuaire de l'éducation).
import os, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/fr_ec4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except urllib.error.HTTPError as e:
            err = Exception(f"HTTP {e.code}: {e.read()[:400]!r}"); time.sleep(5)
        except Exception as e:
            err = e; time.sleep(10)
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-900:]}\n\n")
    log.flush()
def save(name, u):
    b = get(u); open(f"{OUT}/{name}", "wb").write(b); return f"{len(b)} bytes; head {b[:400]!r}"
api = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/"
step("Pupils by school (with school id)", lambda: save("fr_ecoles_2025_uai.csv", api + "fr-en-ecoles-effectifs-nb_classes/exports/csv?" + urllib.parse.urlencode(
    {"select": "numero_ecole,secteur,nombre_total_eleves", "where": "rentree_scolaire = date'2025'", "delimiter": ";"})))
step("School directory: id -> INSEE commune", lambda: save("fr_annuaire_uai_commune.csv", api + "fr-en-annuaire-education/exports/csv?" + urllib.parse.urlencode(
    {"select": "identifiant_de_l_etablissement,code_commune,nom_commune", "delimiter": ";"})))
log.close()

# --- Ecuador ---
exec(compile(open('fetch/ec_amie.py').read(), 'ec_amie', 'exec'), {'__name__': 'ec'})
