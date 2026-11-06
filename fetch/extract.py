# Temporary: what Peru's and Spain's official data sources offer to a script.
import json, os, re, time, traceback, urllib.request, urllib.parse
OUT = "fetch/out/pe_es1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.status, r.headers.get("Content-Type", ""), r.read()
def probe(name, u, save=None, n=1500):
    try:
        s, ct, b = get(u)
        if save: open(f"{OUT}/{save}", "wb").write(b)
        log.write(f"== {name} {s} {ct} {len(b)}\n{b[:n].decode('utf-8','replace')}\n\n")
        return b
    except Exception as e:
        log.write(f"== {name} ERR {str(e)[:300]}\n\n")
    finally:
        log.flush(); time.sleep(1)
# --- Spain: INE tempus API, the ADRH (income atlas) and padrón operations
b = probe("INE operations", "https://servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES", "ine_ops.json", 300)
for op in ("ADRH", "353", "PADRON", "22"):
    probe(f"INE tables of {op}", f"https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/{op}", f"ine_tables_{op}.json", 3000)
# --- geoBoundaries metadata
for iso in ("ESP", "PER"):
    probe(f"geoBoundaries {iso}", f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/ALL/", f"gb_{iso}.json", 2500)
# --- Peru: open data portal (DKAN) and INEI
for q in ("pobreza distrital", "mapa de pobreza", "matricula distrito", "padron instituciones educativas"):
    probe(f"datosabiertos.gob.pe search {q}", "https://www.datosabiertos.gob.pe/api/3/action/package_search?rows=20&q=" + urllib.parse.quote(q), f"pe_search_{q.replace(' ','_')}.json", 2500)
probe("INEI home", "https://www.inei.gob.pe/", None, 300)
probe("ESCALE", "https://escale.minedu.gob.pe/", None, 300)
probe("ESCALE padron", "https://escale.minedu.gob.pe/uee/-/document_library_display/GMv7/view/958881", None, 600)
probe("SIGMED/datos abiertos minedu", "https://datosabiertos.minedu.gob.pe/", None, 600)
log.close()
