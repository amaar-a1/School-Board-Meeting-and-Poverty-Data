# Temporary: Chile 2024 poverty and latest enrollment; Colombia poverty, enrollment, borders.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/clph2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research script; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
log = []
def get(url, name=None):
    time.sleep(1.5)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300); d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {r.geturl()[:200]}"); return d, r.geturl()
    except Exception as e:
        log.append(f"FAIL {url[:200]}: {e}"); return None, url
def links(d, base, pat):
    return sorted({urllib.parse.urljoin(base, l.decode(errors="ignore")) for l in re.findall(rb'href="([^"]+)"', d or b"") if re.search(pat, l.decode(errors="ignore"), re.I)})
d, f = get("https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-2024", "cl_2024.html")
for l in [x for x in links(d, f, r"\.xlsx?$")][:4]: get(l, "cl_" + os.path.basename(urllib.parse.urlparse(l).path)[:80])
d, f = get("https://datosabiertos.mineduc.cl/resumen-de-matricula-por-establecimiento-educacional/")
rars = [x for x in links(d, f, r"\.(rar|zip|csv)$")]
open(f"{OUT}/cl_enrol_links.txt", "w").write("\n".join(rars))
latest = sorted(rars, key=lambda x: re.findall(r"20\d\d", x)[-1] if re.findall(r"20\d\d", x) else "")[-1:]
for l in latest: get(l, "cl_" + os.path.basename(urllib.parse.urlparse(l).path))
# Colombia
d, _ = get("https://www.geoboundaries.org/api/current/gbOpen/COL/ADM2/", "gb_COL_ADM2.json")
if d:
    j = json.loads(d); log.append(f"COL ADM2 {j.get('admUnitCount')}"); get(j["simplifiedGeometryGeoJSON"], "gb_COL_ADM2_simplified.geojson")
for u in ("https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/pobreza-multidimensional",
          "https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/pobreza-y-desigualdad/medida-de-pobreza-multidimensional-municipal-de-fuente-censal"):
    d, f = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    found = links(d, f, r"\.xlsx?$|municipal|censal")
    open(f"{OUT}/co_poverty_links.txt", "a").write("\n".join(found) + "\n")
    for l in [x for x in found if re.search(r"\.xlsx?$", x) and re.search(r"munic|censal|cnpv", x, re.I)][:3]:
        get(l, "co_" + os.path.basename(urllib.parse.urlparse(l).path)[:80])
# MEN statistics by municipality (Socrata, datos.gov.co)
get("https://www.datos.gov.co/api/catalog/v1?q=estadisticas%20educacion%20preescolar%20basica%20media%20municipio&limit=10", "co_catalog.json")
get("https://www.datos.gov.co/resource/nudc-7mev.json?$limit=5", "co_men_sample.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
