# Temporary: Colombia, MEN establecimientos (cfw5-qzt5): enrollment by municipality and sector, latest year.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/co_sector1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(q):
    u = "https://www.datos.gov.co/resource/cfw5-qzt5.json?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: return json.loads(r.read())
try:
    yrs = get({"$select": "a_o, count(*) as n, sum(total_matricula) as m", "$group": "a_o", "$order": "a_o DESC"}); log.write("years " + json.dumps(yrs) + "\n")
    secs = get({"$select": "cod_sector, count(*) as n", "$group": "cod_sector"}); log.write("sectors " + json.dumps(secs) + "\n")
    y = yrs[0]["a_o"]
    agg = get({"$select": "cod_dane_municipio, cod_sector, sum(total_matricula) as m", "$where": f"a_o='{y}'", "$group": "cod_dane_municipio, cod_sector", "$limit": 50000})
    json.dump({"year": y, "rows": agg}, open(f"{OUT}/co_sector_{y}.json", "w")); log.write(f"agg {y}: {len(agg)} rows {agg[:3]}\n")
except Exception as e: log.write(f"ERR {e} {getattr(e, 'read', lambda: b'')()[:300]}\n")
log.close()
