# Temporary: Colombia enrollment by municipality (MEN sedes), Brazil (IBGE indicators), Valencia/Euskadi search.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/enr_find2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    yrs = json.loads(get("https://www.datos.gov.co/resource/x5ay-984n.json?" + urllib.parse.urlencode({"$select": "año, count(*), sum(total_matricula)", "$group": "año", "$order": "año DESC"})))
    log.write("CO years " + json.dumps(yrs) + "\n")
    m = json.loads(get("https://www.datos.gov.co/api/views/x5ay-984n.json")); log.write("CO cols " + json.dumps([c["fieldName"] for c in m["columns"]]) + "\n")
    y = yrs[0]["a_o"] if "a_o" in yrs[0] else list(yrs[0].values())[0]
    ycol = "a_o" if "a_o" in yrs[0] else "año"
    sec = next((c["fieldName"] for c in m["columns"] if "sector" in c["fieldName"]), None)
    agg = json.loads(get("https://www.datos.gov.co/resource/x5ay-984n.json?" + urllib.parse.urlencode({"$select": f"cod_dane_municipio, {sec}, sum(total_matricula)", "$where": f"{ycol}='{y}'", "$group": f"cod_dane_municipio, {sec}", "$limit": 50000})))
    json.dump({"year": y, "rows": agg}, open(f"{OUT}/co_matricula.json", "w")); log.write(f"CO agg year {y}: {len(agg)} rows\n")
except Exception as e: log.write(f"ERR CO {e}\n")
try:
    ind = json.loads(get("https://servicodados.ibge.gov.br/api/v1/pesquisas/13/indicadores"))
    def walk(xs, d=0):
        for x in xs:
            log.write(f"BR ind {'  '*d}{x['id']} {x['indicador']} {x.get('unidade',{}).get('id','')}\n"); walk(x.get("children", []), d + 1)
    walk(ind)
except Exception as e: log.write(f"ERR BR ind {e}\n")
for q in ["alumnado matriculado centros", "alumnado infantil primaria secundaria municipio", "alumnos ensenanzas regimen general"]:
    try:
        d = json.loads(get("https://dadesobertes.gva.es/api/3/action/package_search?rows=8&q=" + urllib.parse.quote(q)))
        for p in d["result"]["results"]: log.write(f"GVA | {p['name']} | {p.get('title')}\n")
    except Exception as e: log.write(f"ERR GVA {e}\n")
log.close()
