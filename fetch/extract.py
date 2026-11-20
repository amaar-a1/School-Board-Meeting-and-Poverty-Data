# Probe sources for Argentina and Israel.
import os, urllib.request, urllib.parse, json, re, time
OUT = "fetch/out/arisr"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, keep=True, timeout=180):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"== {name} OK {len(b)} {url}\n"); log.flush(); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush(); return None
    finally: time.sleep(2)
# Argentina
get("ar_indec_pobreza.html", "https://www.indec.gob.ar/indec/web/Nivel4-Tema-4-46-152")
get("ar_gb_adm1.json", "https://www.geoboundaries.org/api/current/gbOpen/ARG/ADM1/")
get("ar_gb_adm2.json", "https://www.geoboundaries.org/api/current/gbOpen/ARG/ADM2/")
get("ar_anuarios.html", "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/anuarios")
get("ar_datos_matricula.json", "https://datos.gob.ar/api/3/action/package_search?q=matricula&rows=30")
get("ar_datos_pobreza.json", "https://datos.gob.ar/api/3/action/package_search?q=pobreza&rows=30")
get("ar_georef_prov.json", "https://apis.datos.gob.ar/georef/api/provincias?campos=id,nombre&max=30")
# Israel
for q in ["רשויות מקומיות", "מדד חברתי כלכלי", "גבולות שיפוט", "מוסדות חינוך", "תלמידים", "local authorities"]:
    get(f"il_ckan_{re.sub(r'[^a-z0-9]+','_',q.encode('unicode_escape').decode().lower())[:40]}.json",
        "https://data.gov.il/api/3/action/package_search?rows=40&q=" + urllib.parse.quote(q))
get("il_gb_adm1.json", "https://www.geoboundaries.org/api/current/gbOpen/ISR/ADM1/")
get("il_gb_adm2.json", "https://www.geoboundaries.org/api/current/gbOpen/ISR/ADM2/")
get("il_cbs_la.html", "https://www.cbs.gov.il/he/publications/Pages/2024/%D7%94%D7%A8%D7%A9%D7%95%D7%99%D7%95%D7%AA-%D7%94%D7%9E%D7%A7%D7%95%D7%9E%D7%99%D7%95%D7%AA-%D7%91%D7%99%D7%A9%D7%A8%D7%90%D7%9C-2022.aspx")
get("il_cbs_home.html", "https://www.cbs.gov.il/he/Pages/default.aspx")
get("il_btl_poverty.html", "https://www.btl.gov.il/Publications/oni_report/Pages/default.aspx")
# OSM Israel local authority boundaries (admin_level 8) count only
q = '[out:json][timeout:120];area["ISO3166-1"="IL"][admin_level=2]->.a;rel(area.a)[boundary=administrative][admin_level~"^(6|8)$"];out tags;'
get("il_osm_tags.json", "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q), timeout=300)
q = '[out:json][timeout:120];area["ISO3166-1"="AR"][admin_level=2]->.a;rel(area.a)[boundary=administrative][admin_level=4];out tags;'
get("ar_osm_prov_tags.json", "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q), timeout=300)
