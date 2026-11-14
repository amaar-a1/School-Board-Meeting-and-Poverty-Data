# Temporary: (1) Census Bureau 2024 Gazetteer files: land area of every school district (unified, elementary,
# secondary); (2) Saint-Pierre-et-Miquelon's communes: legal population and area (geo.api.gouv.fr, INSEE).
import csv, io, json, os, urllib.request, zipfile
OUT = "fetch/out/gaz1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
land = {}
for kind in ("unsd", "elsd", "scsd"):
    for y in ("2024", "2023"):
        try:
            z = zipfile.ZipFile(io.BytesIO(get(f"https://www2.census.gov/geo/docs/maps-data/data/gazetteer/{y}_Gazetteer/{y}_Gaz_{kind}_national.zip")))
            name = z.namelist()[0]
            rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1"), delimiter="\t"))
            rows = [{k.strip(): v for k, v in r.items()} for r in rows]
            for r in rows: land.setdefault(r["GEOID"], round(float(r["ALAND"]) / 1e6, 3))
            log.write(f"{kind} {y}: {len(rows)} rows, cols {list(rows[0])}\n"); break
        except Exception as e: log.write(f"ERR {kind} {y} {str(e)[:120]}\n")
json.dump({"source": "Census Bureau, 2024 Gazetteer files (unified, elementary and secondary school districts), ALAND (land area, m²) in km²", "land_km2": land}, open(f"{OUT}/us_gazetteer_land_km2.json", "w"))
try:
    b = get("https://geo.api.gouv.fr/communes?codeDepartement=975&fields=nom,code,population,surface", 60); log.write("SPM " + b.decode() + "\n")
except Exception as e: log.write(f"ERR SPM {e}\n")
log.close()
