# Temporary: Spain (INE 2021 census tables on people studying, by municipality) and Croatia (data.gov.hr: pupils by school).
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/esh1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=180):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
# INE: operations list, then census 2021 tables whose names mention studies
try:
    ops = json.loads(get("https://servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES"))
    cen = [o for o in ops if "enso" in o.get("Nombre", "") and ("2021" in o.get("Nombre", "") or "Población y Viviendas" in o.get("Nombre", ""))]
    log.write("census ops: " + json.dumps([(o["Id"], o.get("Codigo"), o["Nombre"]) for o in cen], ensure_ascii=False) + "\n")
    for o in cen:
        tabs = json.loads(get(f"https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{o['Id']}"))
        hits = [(t["Id"], t["Nombre"]) for t in tabs if any(w in t["Nombre"].lower() for w in ("estudi", "cursa", "formación", "educa"))]
        log.write(f"op {o['Id']} {len(tabs)} tables; study tables: " + json.dumps(hits[:60], ensure_ascii=False) + "\n")
except Exception as e: log.write(f"ERR ine {str(e)[:200]}\n")
log.flush()
for q in ("učenici", "osnovne škole učenici", "škole"):
    try:
        d = json.loads(get("https://data.gov.hr/ckan/api/3/action/package_search?rows=30&q=" + urllib.parse.quote(q)))["result"]
        log.write(f"== hr '{q}': {d['count']}\n")
        for p in d["results"]:
            log.write(f"  {p['name']} | {p.get('title')} | {p.get('organization', {}) and p['organization'].get('title')}\n")
            for r in p.get("resources", [])[:4]: log.write(f"      {r.get('format')} | {r['url'][:150]}\n")
    except Exception as e: log.write(f"ERR hr {q} {str(e)[:150]}\n")
log.close()
