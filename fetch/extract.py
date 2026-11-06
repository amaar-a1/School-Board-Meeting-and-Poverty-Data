# Temporary: Spain's ADRH poverty-by-age table shape (one province), and Peru's district sources.
import json, os, re, time, urllib.request, urllib.parse
OUT = "fetch/out/pe_es2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.status, r.headers.get("Content-Type", ""), r.read()
def probe(name, u, save=None, n=1500):
    try:
        s, ct, b = get(u)
        if save: open(f"{OUT}/{save}", "wb").write(b)
        log.write(f"== {name} {s} {ct} {len(b)}\n{b[:n].decode('utf-8','replace')}\n\n"); return b
    except Exception as e: log.write(f"== {name} ERR {str(e)[:300]}\n\n")
    finally: log.flush(); time.sleep(1)
# Spain: series metadata and last-period data of one table (the first id), to see the dimensions
probe("ES table 30662 metadata", "https://servicios.ine.es/wstempus/js/ES/TABLA/30662", "es_30662_meta.json", 1500)
probe("ES table 30662 series (first page)", "https://servicios.ine.es/wstempus/js/ES/SERIES_TABLA/30662?page=1", "es_30662_series.json", 3000)
probe("ES table 30662 data nult=1", "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/30662?nult=1&tip=A", "es_30662_data.json", 2500)
# Peru: district borders (OCHA COD-AB on HDX), INEI poverty map pages, ESCALE downloads
probe("HDX Peru COD-AB", "https://data.humdata.org/api/3/action/package_show?id=cod-ab-per", "hdx_per.json", 4000)
for q in ("mapa de pobreza distrital", "pobreza monetaria distrital"):
    probe(f"INEI search {q}", "https://www.inei.gob.pe/buscador/?tbusqueda=" + urllib.parse.quote(q), f"inei_{q[:12]}.html", 200)
probe("INEI poverty map 2018 book", "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1718/Libro.pdf", None, 100)
b = probe("ESCALE padron page", "https://escale.minedu.gob.pe/web/inicio/padron-de-iiee", "escale_padron.html", 200)
probe("ESCALE magnitudes", "https://escale.minedu.gob.pe/magnitudes", "escale_mag.html", 200)
probe("ESCALE descargas", "https://escale.minedu.gob.pe/uee/-/document_library_display/GMv7/view/5384052", "escale_desc.html", 200)
log.close()
