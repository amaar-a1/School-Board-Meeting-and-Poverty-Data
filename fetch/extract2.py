# Round 31: Paraguay: INE district poverty map, district projections, NBI; MEC open enrollment data; borders.
import os, json, urllib.request, urllib.parse, time, http.cookiejar, re
OUT = "fetch/out/c31"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=200e6, timeout=300):
    try:
        b = opener.open(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%"), headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:200]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
B = "https://www.ine.gov.py/"
for n, p in [("py_pov_dist.xlsx", "Publicaciones/Biblioteca/documento/295/Cuadro-Incidencia-Pobreza_Monetaria_Distrital.xlsx"),
             ("py_pov_dist_method.pdf", "Publicaciones/Biblioteca/documento/295/Documento metodologico mapa de pobreza distrital.pdf"),
             ("py_pov_dist_summary.pdf", "Publicaciones/Biblioteca/documento/295/Resumen Ejecutivo Mapa de Pobreza Monetaria Distrital.pdf"),
             ("py_proj_dist.xlsx", "Publicaciones/Biblioteca/documento/284/Estimaciones y proyecciones Distrital. Revisión 2025.xlsx"),
             ("py_ipm_dist_method.pdf", "Publicaciones/Biblioteca/documento/330/INFORME METODOLOGICO IPM DISTRITAL.pdf"),
             ("py_ipm_dist_pres.pdf", "Publicaciones/Biblioteca/documento/330/Presentación IPM Distrital.pdf"),
             ("py_nbi.xlsx", "Publicaciones/Biblioteca/documento/262/Paraguay.Hogares_por_Necesidades_Basicas_Insatisfechas(NBI).xlsx")]:
    get(n, B + p)
get("py_pub330.html", B + "default.php?publicacion=330")
for a in ["ADM2", "ADM1"]:
    get(f"py_gb_{a}.geojson", f"https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/PRY/{a}/geoBoundaries-PRY-{a}_simplified.geojson")
# MEC open data
h = get("py_mec_home.html", "https://datos.mec.gov.py/")
get("py_mec_api.json", "https://datos.mec.gov.py/api/3/action/package_search?q=matricula&rows=50")
get("py_mec_data.html", "https://datos.mec.gov.py/data")
try:
    for u in sorted(set(re.findall(r'href="([^"]*(?:matricul|establecimiento)[^"]*)"', (h or b"").decode("utf-8", "ignore"), re.I)))[:30]:
        log.write(f"LINK {u}\n")
except Exception as e: log.write(f"links ERR {e}\n")
log.close()
