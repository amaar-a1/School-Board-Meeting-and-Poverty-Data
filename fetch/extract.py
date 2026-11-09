# Temporary: Catalonia pupils by municipality (Socrata aggregate) and Madrid municipal pupils CSV.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/es_reg2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    m = json.loads(get("https://analisi.transparenciacatalunya.cat/api/views/xvme-26kg.json"))
    cols = [(c["fieldName"], c["name"]) for c in m["columns"]]
    log.write("CAT cols " + json.dumps(cols, ensure_ascii=False) + "\n")
    names = {n: f for f, n in cols}
    mun = next(f for f, n in cols if "municipi" in n.lower() and "codi" in n.lower())
    tot = next(f for f, n in cols if n.strip().lower() in ("matrícules. total", "matrícules total", "matrícules. total ")) if any("total" in n.lower() for f, n in cols) else None
    log.write(f"mun={mun} tot={tot}\n")
    yrs = json.loads(get("https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json?" + urllib.parse.urlencode({"$select": "curs, count(*)", "$group": "curs", "$order": "curs DESC", "$limit": 5})))
    log.write("years " + json.dumps(yrs) + "\n")
    cur = yrs[0]["curs"]
    q = {"$select": f"{mun}, nom_ensenyament, sum({tot})", "$where": f"curs='{cur}'", "$group": f"{mun}, nom_ensenyament", "$limit": 50000}
    agg = json.loads(get("https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json?" + urllib.parse.urlencode(q)))
    json.dump({"curs": cur, "rows": agg}, open(f"{OUT}/cat_mun.json", "w"), ensure_ascii=False)
    log.write(f"CAT agg {len(agg)} rows\n")
except Exception as e: log.write(f"ERR CAT {e}\n")
try:
    d = json.loads(get("https://datos.comunidad.madrid/api/3/action/package_show?id=alumnos_no_universitarios_por_tipo_y_regimen"))
    for r in d["result"]["resources"]:
        log.write(f"MAD res {r.get('format')} {r.get('name')} {r['url']}\n")
        if r.get("format", "").upper() == "CSV":
            b = get(r["url"]); open(f"{OUT}/mad_{r['id'][:8]}.csv", "wb").write(b); log.write(f"  {len(b)} bytes\n")
except Exception as e: log.write(f"ERR MAD {e}\n")
log.close()
