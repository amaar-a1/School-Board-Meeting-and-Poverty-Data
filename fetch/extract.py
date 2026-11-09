# Temporary: find school enrollment files for Peru (MINEDU censo educativo / padrón) and the Philippines (DepEd).
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/enr1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
q = {"pe_datosabiertos.json": "https://www.datosabiertos.gob.pe/api/3/action/package_search?q=matricula%20minedu&rows=40",
     "pe_datosabiertos2.json": "https://www.datosabiertos.gob.pe/api/3/action/package_search?q=censo%20educativo&rows=40",
     "pe_escale.html": "https://escale.minedu.gob.pe/padron-de-iiee",
     "pe_escale_datos.html": "https://escale.minedu.gob.pe/uee/-/document_library_display/GMv7/view/958881",
     "ph_hdx.json": "https://data.humdata.org/api/3/action/package_search?q=philippines%20school%20enrollment&rows=30",
     "ph_hdx2.json": "https://data.humdata.org/api/3/action/package_search?q=deped%20schools%20masterlist&rows=30",
     "ph_datagov.json": "https://data.gov.ph/api/3/action/package_search?q=enrollment&rows=40",
     "ph_deped.html": "https://www.deped.gov.ph/alternative-learning-system/resources/downloads/datasets/"}
for name, u in q.items():
    try: b = get(u); open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
