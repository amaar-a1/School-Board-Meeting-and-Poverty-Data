# Temporary: Colombia enrollment by municipality (MEN sedes) with field names from metadata; GVA escolarización; IBGE retry.
import json, os, urllib.parse, urllib.request, time
OUT = "fetch/out/enr_find3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    m = json.loads(get("https://www.datos.gov.co/api/views/x5ay-984n.json"))
    cols = {c["name"]: c["fieldName"] for c in m["columns"]}; log.write("CO cols " + json.dumps(cols, ensure_ascii=False) + "\n")
    yc = next(v for k, v in cols.items() if k.upper().startswith("A") and "O" in k.upper() and len(k) <= 4)
    mc = cols["COD_DANE_MUNICIPIO"]; tc = cols["TOTAL_MATRICULA"]; sc = cols.get("CTE_ID_SECTOR")
    yrs = json.loads(get("https://www.datos.gov.co/resource/x5ay-984n.json?" + urllib.parse.urlencode({"$select": f"{yc}, count(*) as n", "$group": yc, "$order": f"{yc} DESC"})))
    log.write("CO years " + json.dumps(yrs) + "\n")
    y = yrs[0][yc]
    agg = json.loads(get("https://www.datos.gov.co/resource/x5ay-984n.json?" + urllib.parse.urlencode({"$select": f"{mc}, {sc}, sum({tc}) as pupils, count(*) as sedes", "$where": f"{yc}='{y}'", "$group": f"{mc}, {sc}", "$limit": 50000})))
    json.dump({"year": y, "cols": cols, "rows": agg}, open(f"{OUT}/co_matricula.json", "w"), ensure_ascii=False); log.write(f"CO agg year {y}: {len(agg)} rows; sample {agg[:3]}\n")
except Exception as e: log.write(f"ERR CO {e}\n")
for y in (2025, 2024, 2023, 2022, 2021, 2020, 2019):
    try:
        d = json.loads(get(f"https://dadesobertes.gva.es/api/3/action/package_show?id=edu-alu-gen-{y}"))
        for r in d["result"]["resources"]: log.write(f"GVA {y} {r.get('format')} {r.get('name')} {r['url']}\n")
        r = next(r for r in d["result"]["resources"] if r.get("format", "").upper() == "CSV")
        b = get(r["url"]); open(f"{OUT}/gva_{y}.csv", "wb").write(b); log.write(f"  {len(b)} bytes; head {b[:600]!r}\n"); break
    except Exception as e: log.write(f"GVA {y} ERR {str(e)[:100]}\n")
for i in range(2):
    try:
        ind = json.loads(get("https://servicodados.ibge.gov.br/api/v1/pesquisas/13/indicadores", 120))
        def walk(xs, d=0):
            for x in xs:
                log.write(f"BR ind {'  '*d}{x['id']} {x['indicador']}\n"); walk(x.get("children", []), d + 1)
        walk(ind); break
    except Exception as e: log.write(f"ERR BR ind {e}\n"); time.sleep(20)
log.close()
